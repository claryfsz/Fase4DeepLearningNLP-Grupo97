"""Preparação da base de conhecimento (parte da MC).

Etapas:
1. Seleção: carrega as avaliações (olist_order_reviews_dataset.csv).
2. Tratamento de ausentes: título e comentário vazios viram string vazia;
   avaliações sem nenhum texto são descartadas (não há o que recuperar).
3. Limpeza: normalização Unicode, remoção de quebras de linha e espaços
   repetidos, descarte de textos curtos demais para carregar informação.
4. Duplicatas: remove review_id repetido e agrupa textos idênticos com a
   mesma nota, guardando quantas vezes apareceram (n_duplicatas).
5. Organização: cada avaliação vira um documento "título. comentário"
   com metadados (nota, data, categoria, situação da entrega).

Uso:
    python -m src.data_prep
Gera data/processed/documentos.parquet e docs/relatorio_base.md.
"""
import re
import unicodedata

import numpy as np
import pandas as pd

from src import config


# ---------------------------------------------------------------- limpeza
def limpar_texto(texto) -> str:
    """Normaliza um campo de texto livre. Ausentes viram string vazia."""
    if pd.isna(texto):
        return ""
    texto = unicodedata.normalize("NFC", str(texto))
    texto = re.sub(r"[\r\n\t]+", " ", texto)       # quebras de linha
    texto = re.sub(r"\s{2,}", " ", texto)           # espaços repetidos
    texto = texto.strip(" .,;:-")
    return texto.strip()


def montar_documento(titulo: str, comentario: str) -> str:
    """Une título e comentário em um único texto.

    O título costuma ser curto ("Recomendo", "Não recebi"), mas resume a
    opinião; por isso entra antes do comentário, separado por ponto.
    """
    partes = [p for p in (titulo, comentario) if p]
    return ". ".join(partes)


# ------------------------------------------------------- metadados extras
def _formatar_categoria(nome) -> str:
    if pd.isna(nome) or not str(nome).strip():
        return "desconhecida"
    return str(nome).replace("_", " ").strip()


def verificar_arquivos() -> None:
    """Interrompe com uma mensagem clara se faltar algum CSV em data/raw."""
    faltando = [p.name for p in config.ARQUIVOS_NECESSARIOS if not p.exists()]
    if faltando:
        lista = "\n".join(f"  - {nome}" for nome in faltando)
        raise SystemExit(
            f"\n[erro] Arquivo(s) não encontrado(s) em {config.RAW_DIR}:\n{lista}\n\n"
            f"Baixe o dataset em {config.KAGGLE_URL}\n"
            f"(é preciso fazer login no Kaggle), descompacte e copie esses arquivos\n"
            f"para a pasta data/raw/. Veja a seção \"Dados\" do README.\n"
        )


def carregar_metadados_pedidos() -> pd.DataFrame:
    """Junta pedidos, itens e produtos para obter categoria e entrega por order_id."""
    orders = pd.read_csv(
        config.ORDERS_CSV,
        parse_dates=["order_purchase_timestamp", "order_delivered_customer_date",
                     "order_estimated_delivery_date"],
    )
    items = pd.read_csv(config.ORDER_ITEMS_CSV, usecols=["order_id", "product_id"])
    products = pd.read_csv(config.PRODUCTS_CSV, usecols=["product_id", "product_category_name"])

    # Um pedido pode ter vários itens: usamos a categoria mais frequente do pedido.
    itens_cat = items.merge(products, on="product_id", how="left")
    categoria = (
        itens_cat.groupby("order_id")["product_category_name"]
        .agg(lambda s: s.mode().iloc[0] if not s.mode().empty else None)
        .rename("categoria")
        .map(_formatar_categoria)
    )

    entregue = orders["order_delivered_customer_date"]
    estimada = orders["order_estimated_delivery_date"]
    situacao = pd.Series("nao_entregue", index=orders.index)
    situacao[entregue.notna() & (entregue <= estimada)] = "no_prazo"
    situacao[entregue.notna() & (entregue > estimada)] = "atrasada"

    meta = pd.DataFrame({
        "order_id": orders["order_id"],
        "status_pedido": orders["order_status"].fillna("desconhecido"),
        "entrega": situacao,
        # arredonda para cima: 5 horas de atraso contam como 1 dia
        "dias_atraso": np.ceil((entregue - estimada).dt.total_seconds() / 86400),
    }).merge(categoria, on="order_id", how="left")
    meta["categoria"] = meta["categoria"].fillna("desconhecida")
    return meta


# --------------------------------------------------------------- pipeline
def preparar_base() -> tuple[pd.DataFrame, dict]:
    stats: dict = {}
    verificar_arquivos()

    df = pd.read_csv(config.REVIEWS_CSV)
    stats["total_avaliacoes"] = len(df)
    stats["sem_titulo"] = int(df["review_comment_title"].isna().sum())
    stats["sem_comentario"] = int(df["review_comment_message"].isna().sum())
    stats["dist_notas_total"] = df["review_score"].value_counts().sort_index().to_dict()

    # 1) review_id duplicado (o mesmo review aparece ligado a mais de um pedido)
    df = df.drop_duplicates(subset="review_id", keep="first")
    stats["apos_dedup_review_id"] = len(df)

    # 2) limpeza e montagem do documento
    df["titulo"] = df["review_comment_title"].map(limpar_texto)
    df["comentario"] = df["review_comment_message"].map(limpar_texto)
    df["texto"] = [montar_documento(t, c) for t, c in zip(df["titulo"], df["comentario"])]

    # 3) ausentes: sem título e sem comentário -> não há conteúdo textual
    df = df[df["texto"].str.len() > 0]
    stats["com_algum_texto"] = len(df)

    # 4) textos curtos demais para carregar informação
    df = df[df["texto"].str.len() >= config.MIN_CHARS]
    stats["apos_filtro_tamanho"] = len(df)

    # 5) textos idênticos com a mesma nota: mantém 1 e registra a frequência,
    #    para não poluir o top-k com cópias e não perder a noção de volume.
    df["chave_dup"] = df["texto"].str.lower() + "||" + df["review_score"].astype(str)
    contagem = df.groupby("chave_dup")["review_id"].transform("count")
    df["n_duplicatas"] = contagem.astype(int)
    df = df.drop_duplicates(subset="chave_dup", keep="first").drop(columns="chave_dup")
    stats["apos_dedup_texto"] = len(df)

    # 6) metadados
    df["data"] = pd.to_datetime(df["review_creation_date"]).dt.strftime("%Y-%m-%d")
    df["ano_mes"] = df["data"].str[:7]
    df = df.merge(carregar_metadados_pedidos(), on="order_id", how="left")
    for col, padrao in [("categoria", "desconhecida"), ("entrega", "desconhecida"),
                        ("status_pedido", "desconhecido")]:
        if col not in df:
            df[col] = padrao
        df[col] = df[col].fillna(padrao)
    if "dias_atraso" not in df:
        df["dias_atraso"] = pd.NA

    df = df.rename(columns={"review_score": "score"})
    colunas = ["review_id", "order_id", "score", "data", "ano_mes", "categoria",
               "entrega", "dias_atraso", "status_pedido", "n_duplicatas",
               "titulo", "comentario", "texto"]
    df = df[colunas].reset_index(drop=True)

    stats["documentos_finais"] = len(df)
    stats["dist_notas_final"] = df["score"].value_counts().sort_index().to_dict()
    stats["tamanho_texto"] = df["texto"].str.len().describe().round(1).to_dict()
    stats["dist_entrega"] = df["entrega"].value_counts().to_dict()
    stats["top_categorias"] = df["categoria"].value_counts().head(10).to_dict()
    return df, stats


def escrever_relatorio(stats: dict) -> str:
    total = stats["total_avaliacoes"]
    pct = lambda n: f"{n / total:.1%}"  # noqa: E731
    linhas = [
        "# Relatório da base de conhecimento",
        "",
        "Gerado automaticamente por `python -m src.data_prep`.",
        "",
        "## Funil de preparação",
        "",
        "| Etapa | Avaliações | % do total |",
        "|---|---:|---:|",
        f"| Base original | {total:,} | 100% |",
        f"| Após remover `review_id` duplicado | {stats['apos_dedup_review_id']:,} | {pct(stats['apos_dedup_review_id'])} |",
        f"| Com título ou comentário | {stats['com_algum_texto']:,} | {pct(stats['com_algum_texto'])} |",
        f"| Com pelo menos {config.MIN_CHARS} caracteres | {stats['apos_filtro_tamanho']:,} | {pct(stats['apos_filtro_tamanho'])} |",
        f"| Após agrupar textos idênticos (documentos indexados) | {stats['apos_dedup_texto']:,} | {pct(stats['apos_dedup_texto'])} |",
        "",
        "## Valores ausentes na base original",
        "",
        f"- Sem título: {stats['sem_titulo']:,} ({pct(stats['sem_titulo'])})",
        f"- Sem comentário: {stats['sem_comentario']:,} ({pct(stats['sem_comentario'])})",
        "",
        "## Distribuição de notas",
        "",
        "| Nota | Base original | Documentos indexados |",
        "|---|---:|---:|",
    ]
    for nota in sorted(stats["dist_notas_total"]):
        linhas.append(f"| {nota} | {stats['dist_notas_total'][nota]:,} | "
                      f"{stats['dist_notas_final'].get(nota, 0):,} |")
    t = stats["tamanho_texto"]
    linhas += [
        "",
        "## Tamanho dos documentos (caracteres)",
        "",
        f"Média {t['mean']}, mediana {t['50%']}, mínimo {t['min']:.0f}, máximo {t['max']:.0f}.",
        "",
        "## Situação da entrega (documentos indexados)",
        "",
    ]
    linhas += [f"- {k}: {v:,}" for k, v in stats["dist_entrega"].items()]
    linhas += ["", "## 10 categorias com mais documentos", ""]
    linhas += [f"- {k}: {v:,}" for k, v in stats["top_categorias"].items()]
    return "\n".join(linhas) + "\n"


def main():
    df, stats = preparar_base()
    config.PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    df.to_parquet(config.DOCUMENTS_PARQUET, index=False)
    config.EDA_REPORT.write_text(escrever_relatorio(stats), encoding="utf-8")
    print(f"{len(df):,} documentos salvos em {config.DOCUMENTS_PARQUET}")
    print(f"Relatório em {config.EDA_REPORT}")


if __name__ == "__main__":
    main()
