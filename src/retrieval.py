"""Recuperação de evidências para o pipeline RAG.

Função principal: `buscar_evidencias(pergunta)`, chamada pelo pipeline dentro de `responder()`.

Estratégia:
1. Intenção: detecta se a pergunta é sobre problemas (filtra nota <= 2), elogios
   (nota >= 4) ou neutra (sem filtro de nota).
2. Tema: detecta se a pergunta cita um tema (entrega, qualidade, atendimento,
   produto errado/incompleto, preço).
3. Multi-query: perguntas amplas ("quais os principais problemas?") têm
   similaridade baixa e puxam avaliações pelas palavras ("problema", "cliente").
   Por isso a pergunta é expandida em subconsultas concretas por tema, que
   chegam a ~0,95 de similaridade. A pergunta original também é buscada.
4. Fusão: junta os resultados por review_id (fica a maior similaridade),
   descarta os abaixo do limiar de relevância e seleciona em rodízio entre as
   consultas, para que todo tema com evidência apareça no contexto.
5. Status: se a própria pergunta original não chega ao LIMIAR_ESCOPO, ela está
   fora do escopo da base e o status é "sem_evidencia". As subconsultas não contam
   para isso, porque elas sempre encontram algo.
"""
import re
import unicodedata
from functools import lru_cache

import chromadb

from src import config
from src.embeddings import embed_query

# Calibrado com testes manuais (ver docs/base_de_conhecimento.md):
# fora do escopo ~0,84 | perguntas amplas ~0,87-0,88 | específicas ~0,95
LIMIAR_ESCOPO = 0.85
LIMIAR_RELEVANCIA = 0.85
MIN_EVIDENCIAS = 3

# ---------------------------------------------------------------- vocabulário
PADROES_PROBLEMA = [
    r"problema", r"reclama", r"\binsatisf", r"ruim", r"pessim", r"defeit", r"quebr",
    r"atras", r"demor", r"nao (chegou|recebi|entreg)", r"errad", r"negativ", r"falha",
    r"critic", r"nota(s)? baixa", r"cancel", r"devolu", r"estorno", r"\bpior",
    r"decepc", r"frustr",
]
PADROES_ELOGIO = [
    r"elogi", r"positiv", r"\bsatisf", r"\bgost", r"valoriz", r"\bbo(m|a|ns|as)\b",
    r"otim", r"excelen", r"recomend", r"nota(s)? alta", r"destaque", r"\bfeliz",
]
PADROES_AMPLA = [
    r"principa", r"\bmais (frequen|comun|elogi|relat|cit|recorr)", r"padro", r"padrao",
    r"recorren", r"em geral", r"\bquais\b", r"o que os clientes", r"frequen", r"tendenc",
]

TEMAS = {
    "entrega": {
        "padroes": [r"entreg", r"prazo", r"atras", r"demor", r"correio", r"frete", r"chegou", r"rastre"],
        "problema": ["atraso na entrega", "produto não foi entregue",
                     "entrega demorou muito mais que o prazo",
                     "rastreamento sem atualização, produto parado nos correios"],
        "elogio": ["entrega rápida, chegou antes do prazo", "chegou dentro do prazo e bem embalado"],
    },
    "qualidade": {
        "padroes": [r"qualidade", r"defeit", r"quebr", r"material", r"durab", r"estrag", r"funcion"],
        "problema": ["produto chegou quebrado", "produto com defeito, não funciona",
                     "produto de baixa qualidade, material ruim"],
        "elogio": ["produto de ótima qualidade", "material excelente, muito resistente"],
    },
    "atendimento": {
        "padroes": [r"atendiment", r"contato", r"suporte", r"respond", r"vendedor", r"\bsac\b", r"comunica"],
        "problema": ["não consigo contato com a loja, ninguém responde",
                     "atendimento péssimo, não resolvem o problema"],
        "elogio": ["atendimento excelente do vendedor", "loja atenciosa, respondeu rápido"],
    },
    "pedido_errado": {
        "padroes": [r"errad", r"diferente", r"anunciad", r"faltand", r"faltou", r"incomplet", r"troca"],
        "problema": ["recebi o produto errado, diferente do anunciado",
                     "pedido incompleto, faltou um item"],
        "elogio": ["produto igual ao anunciado, conforme a descrição"],
    },
    "financeiro": {
        "padroes": [r"preco", r"valor", r"barat", r"caro", r"estorno", r"reembols", r"custo"],
        "problema": ["cancelei a compra e não recebi o estorno", "cobrança indevida no cartão"],
        "elogio": ["ótimo custo-benefício, preço bom"],
    },
}


def _normalizar(texto: str) -> str:
    sem_acento = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return sem_acento.lower()


def _bate(texto: str, padroes: list[str]) -> bool:
    return any(re.search(p, texto) for p in padroes)


def classificar_intencao(pergunta: str) -> str:
    """'problema', 'elogio' ou 'neutra'."""
    t = _normalizar(pergunta)
    prob, elog = _bate(t, PADROES_PROBLEMA), _bate(t, PADROES_ELOGIO)
    if prob and not elog:
        return "problema"
    if elog and not prob:
        return "elogio"
    return "neutra"


def detectar_temas(pergunta: str) -> list[str]:
    t = _normalizar(pergunta)
    return [nome for nome, tema in TEMAS.items() if _bate(t, tema["padroes"])]


def eh_ampla(pergunta: str) -> bool:
    return _bate(_normalizar(pergunta), PADROES_AMPLA)


def gerar_subconsultas(pergunta: str, intencao: str, temas: list[str]) -> list[str]:
    """Expande perguntas amplas em buscas concretas.

    Perguntas específicas ("produto chegou quebrado") já acham resultados com
    ~0,95 de similaridade e não são expandidas. Perguntas neutras e sem tema
    também não, para que perguntas fora do escopo não ganhem subconsultas que
    sempre acham algo.
    """
    if not eh_ampla(pergunta):
        return []
    lados = ["problema", "elogio"] if intencao == "neutra" else [intencao]
    if temas:  # pergunta ampla sobre um tema: todas as subconsultas do tema
        return [q for nome in temas for lado in lados for q in TEMAS[nome][lado]]
    if intencao == "neutra":
        return []
    # pergunta ampla sem tema: até 2 subconsultas de cada tema
    return [q for tema in TEMAS.values() for q in tema[intencao][:2]]


def montar_filtro(intencao: str, filtros_extras: dict | None = None) -> dict | None:
    condicoes = []
    if intencao == "problema":
        condicoes.append({"score": {"$lte": 2}})
    elif intencao == "elogio":
        condicoes.append({"score": {"$gte": 4}})
    for campo, valor in (filtros_extras or {}).items():
        condicoes.append({campo: valor})
    if not condicoes:
        return None
    return condicoes[0] if len(condicoes) == 1 else {"$and": condicoes}


# ------------------------------------------------------------------ busca
@lru_cache(maxsize=1)
def _colecao():
    client = chromadb.PersistentClient(path=str(config.CHROMA_DIR))
    return client.get_collection(config.COLLECTION_NAME)


def _consultar(texto: str, k: int, where: dict | None) -> list[dict]:
    res = _colecao().query(query_embeddings=[embed_query(texto)], n_results=k, where=where)
    return [
        {"review_id": meta["review_id"], "texto": doc, "similaridade": round(1 - dist, 4),
         "score": meta["score"], "categoria": meta["categoria"], "entrega": meta["entrega"],
         "data": meta["data"], "n_duplicatas": meta["n_duplicatas"]}
        for doc, dist, meta in zip(res["documents"][0], res["distances"][0], res["metadatas"][0])
    ]


def buscar_evidencias(
    pergunta: str,
    k_final: int = 30,
    k_por_consulta: int = 8,
    filtros_extras: dict | None = None,
    subconsultas: list[str] | None = None,
    usar_filtro_nota: bool = True,
) -> dict:
    """Recupera as avaliações que servem de evidência para a pergunta.

    Parâmetros:
        k_final: máximo de evidências devolvidas.
        k_por_consulta: resultados por subconsulta (limita a dominância de um tema).
        filtros_extras: filtros de metadados, ex. {"categoria": "beleza saude"},
            {"entrega": "atrasada"}, {"ano_mes": "2018-03"}.
        subconsultas: permite que o pipeline passe subconsultas geradas pelo LLM;
            se None, usa a expansão por dicionário de temas.
        usar_filtro_nota: desliga o filtro automático de nota.

    Retorno:
        {"status": "ok" | "evidencia_insuficiente" | "sem_evidencia",
         "evidencias": [ {review_id, texto, similaridade, score, categoria, entrega,
                          data, n_duplicatas, encontrada_por: [consultas]} ],
         "similaridade_pergunta": float,   # top-1 da pergunta original
         "intencao": str, "temas": [str], "consultas": [str], "filtro": dict | None}
    """
    intencao = classificar_intencao(pergunta)
    temas = detectar_temas(pergunta)
    where = montar_filtro(intencao if usar_filtro_nota else "neutra", filtros_extras)
    if subconsultas is None:
        subconsultas = gerar_subconsultas(pergunta, intencao, temas)

    # 1) pergunta original: decide se está no escopo
    k_original = k_final if not subconsultas else k_por_consulta
    originais = _consultar(pergunta, k_original, where)
    sim_pergunta = originais[0]["similaridade"] if originais else 0.0

    base = {"similaridade_pergunta": sim_pergunta, "intencao": intencao, "temas": temas,
            "consultas": [pergunta] + subconsultas, "filtro": where}
    if sim_pergunta < LIMIAR_ESCOPO:
        return {**base, "status": "sem_evidencia", "evidencias": []}

    # 2) subconsultas + fusão por review_id
    por_consulta = [(q, _consultar(q, k_por_consulta, where)) for q in subconsultas] + \
                   [(pergunta, originais)]
    fundidas: dict[str, dict] = {}
    for consulta, resultados in por_consulta:
        for r in resultados:
            if r["similaridade"] < LIMIAR_RELEVANCIA:
                continue
            atual = fundidas.get(r["review_id"])
            if atual is None:
                fundidas[r["review_id"]] = {**r, "encontrada_por": [consulta]}
            else:
                atual["encontrada_por"].append(consulta)
                atual["similaridade"] = max(atual["similaridade"], r["similaridade"])

    # 3) seleção em rodízio: cada consulta contribui com seu melhor resultado,
    #    depois o 2º melhor, e assim por diante. Um corte global por similaridade
    #    favorece avaliações curtas e literais ("Produto não entregue" ~0,97) e
    #    elimina temas com relatos mais longos (atendimento ~0,93).
    filas = [[r["review_id"] for r in res if r["review_id"] in fundidas]
             for _, res in por_consulta]
    escolhidos: list[str] = []
    while len(escolhidos) < k_final and any(filas):
        for fila in filas:
            while fila and fila[0] in escolhidos:
                fila.pop(0)
            if fila and len(escolhidos) < k_final:
                escolhidos.append(fila.pop(0))

    evidencias = sorted((fundidas[i] for i in escolhidos),
                        key=lambda e: e["similaridade"], reverse=True)
    status = "ok" if len(evidencias) >= MIN_EVIDENCIAS else (
        "evidencia_insuficiente" if evidencias else "sem_evidencia")
    return {**base, "status": status, "evidencias": evidencias}
