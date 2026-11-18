"""Teste rápido da recuperação (sem LLM), para validar o índice.

Uso:
    python -m scripts.testar_busca "atraso na entrega"
    python -m scripts.testar_busca "produto quebrado" --k 5 --nota-max 2
    python -m scripts.testar_busca "elogios" --categoria "beleza saude"
"""
import argparse

import chromadb

from src import config
from src.embeddings import embed_query


def buscar(pergunta: str, k: int = 5, where: dict | None = None) -> list[dict]:
    client = chromadb.PersistentClient(path=str(config.CHROMA_DIR))
    colecao = client.get_collection(config.COLLECTION_NAME)
    res = colecao.query(query_embeddings=[embed_query(pergunta)], n_results=k, where=where)
    return [
        {"texto": doc, "similaridade": round(1 - dist, 3), **meta}
        for doc, dist, meta in zip(res["documents"][0], res["distances"][0], res["metadatas"][0])
    ]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("pergunta")
    p.add_argument("--k", type=int, default=5)
    p.add_argument("--nota-max", type=int)
    p.add_argument("--nota-min", type=int)
    p.add_argument("--categoria")
    a = p.parse_args()

    filtros = []
    if a.nota_max:
        filtros.append({"score": {"$lte": a.nota_max}})
    if a.nota_min:
        filtros.append({"score": {"$gte": a.nota_min}})
    if a.categoria:
        filtros.append({"categoria": a.categoria})
    where = None if not filtros else filtros[0] if len(filtros) == 1 else {"$and": filtros}

    for i, r in enumerate(buscar(a.pergunta, a.k, where), 1):
        print(f"{i}. [sim={r['similaridade']}] nota {r['score']} | {r['categoria']} | "
              f"entrega {r['entrega']} | {r['review_id'][:8]}")
        print(f"   {r['texto'][:200]}\n")


if __name__ == "__main__":
    main()
