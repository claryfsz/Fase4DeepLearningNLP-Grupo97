"""Mostra o que `buscar_evidencias` faz com uma pergunta (sem LLM).

Uso:
    python -m scripts.testar_evidencias "Quais são os principais problemas relatados pelos clientes?"
    python -m scripts.testar_evidencias "O que os clientes elogiam?" --categoria "beleza saude"
    python -m scripts.testar_evidencias "qual a capital da França?"
"""
import argparse
from collections import Counter

from src.retrieval import buscar_evidencias


def main():
    p = argparse.ArgumentParser()
    p.add_argument("pergunta")
    p.add_argument("--k", type=int, default=30)
    p.add_argument("--categoria")
    p.add_argument("--entrega", choices=["no_prazo", "atrasada", "nao_entregue"])
    a = p.parse_args()

    extras = {k: v for k, v in {"categoria": a.categoria, "entrega": a.entrega}.items() if v}
    r = buscar_evidencias(a.pergunta, k_final=a.k, filtros_extras=extras or None)

    print(f"status: {r['status']} | similaridade da pergunta: {r['similaridade_pergunta']}")
    print(f"intenção: {r['intencao']} | temas: {r['temas'] or '-'} | filtro: {r['filtro']}")
    print("consultas:")
    for q in r["consultas"]:
        print(f"  - {q}")
    cobertura = Counter(q for e in r["evidencias"] for q in e["encontrada_por"])
    print("evidências por consulta:", dict(cobertura) or "-")
    print()
    for i, e in enumerate(r["evidencias"], 1):
        print(f"{i}. [sim={e['similaridade']}] nota {e['score']} | {e['categoria']} | "
              f"entrega {e['entrega']} | x{e['n_duplicatas']} | {e['review_id'][:8]}")
        print(f"   {e['texto'][:180]}")


if __name__ == "__main__":
    main()
