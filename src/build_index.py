"""Geração de embeddings e indexação no ChromaDB (parte da MC).

Uso:
    python -m src.build_index                 # indexa todos os documentos
    python -m src.build_index --amostra 5000  # amostra estratificada por nota

A coleção é persistida em data/chroma e usa distância cosseno.
Cada documento guarda o texto e os metadados combinados com a L:
review_id, score, data, categoria (+ ano_mes, entrega, dias_atraso,
status_pedido, n_duplicatas).
"""
import argparse
import time

import chromadb
import pandas as pd

from src import config
from src.embeddings import embed_passages

CHROMA_LOTE = 2000  # o Chroma limita o tamanho de cada inserção


def amostra_estratificada(df: pd.DataFrame, n: int, seed: int = 42) -> pd.DataFrame:
    """Amostra mantendo a proporção de cada nota (1 a 5)."""
    if n >= len(df):
        return df
    frac = n / len(df)
    return df.groupby("score").sample(frac=frac, random_state=seed).reset_index(drop=True)


def montar_metadados(linha: pd.Series) -> dict:
    meta = {
        "review_id": linha["review_id"],
        "order_id": linha["order_id"],
        "score": int(linha["score"]),
        "data": linha["data"],
        "ano_mes": linha["ano_mes"],
        "categoria": linha["categoria"],
        "entrega": linha["entrega"],
        "status_pedido": linha["status_pedido"],
        "n_duplicatas": int(linha["n_duplicatas"]),
        "tem_titulo": bool(linha["titulo"]),
    }
    # O Chroma não aceita None: só inclui o atraso quando ele existe.
    if pd.notna(linha["dias_atraso"]):
        meta["dias_atraso"] = int(linha["dias_atraso"])
    return meta


def get_collection(recriar: bool = False):
    client = chromadb.PersistentClient(path=str(config.CHROMA_DIR))
    if recriar:
        try:
            client.delete_collection(config.COLLECTION_NAME)
        except Exception:
            pass
    return client.get_or_create_collection(
        name=config.COLLECTION_NAME,
        metadata={"hnsw:space": "cosine", "embedding_model": config.EMBEDDING_MODEL},
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--amostra", type=int, default=None,
                        help="indexa só N documentos (amostra estratificada por nota)")
    args = parser.parse_args()

    df = pd.read_parquet(config.DOCUMENTS_PARQUET)
    if args.amostra:
        df = amostra_estratificada(df, args.amostra)
    print(f"Indexando {len(df):,} documentos com {config.EMBEDDING_MODEL}")

    inicio = time.time()
    vetores = embed_passages(df["texto"].tolist())
    t_embed = time.time() - inicio

    colecao = get_collection(recriar=True)
    metadados = [montar_metadados(l) for _, l in df.iterrows()]
    for i in range(0, len(df), CHROMA_LOTE):
        fim = i + CHROMA_LOTE
        colecao.add(
            ids=df["review_id"].iloc[i:fim].tolist(),
            documents=df["texto"].iloc[i:fim].tolist(),
            embeddings=vetores[i:fim],
            metadatas=metadados[i:fim],
        )
    t_total = time.time() - inicio

    print(f"Embeddings: {t_embed:.0f}s | total: {t_total:.0f}s | "
          f"coleção '{config.COLLECTION_NAME}' com {colecao.count():,} documentos "
          f"em {config.CHROMA_DIR}")


if __name__ == "__main__":
    main()
