"""Faz uma pergunta ao pipeline RAG completo (com Claude) pelo terminal.

Uso:
    python -m scripts.perguntar "Quais reclamações de entrega aparecem com maior frequência?"
    python -m scripts.perguntar "O que os clientes elogiam?" --categoria "beleza saude"
"""
import argparse

from src.rag import responder


def imprimir(r: dict) -> None:
    print(f"\nPergunta: {r['pergunta']}")
    print(f"Status: {r['status']} | similaridade da pergunta: {r['similaridade_pergunta']} "
          f"| intenção: {r['intencao']} | consultas: {len(r['consultas'])}")
    print(f"\n{r['resposta']}\n")
    if r["evidencias_citadas"]:
        print("Evidências citadas:")
        for e in r["evidencias_citadas"]:
            print(f"  [{e['ref']}] ({e['review_id'][:8]}) nota {e['score']} | {e['categoria']} | "
                  f"entrega {e['entrega']} | x{e['n_duplicatas']}: {e['texto'][:160]}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("pergunta")
    p.add_argument("--categoria")
    p.add_argument("--entrega", choices=["no_prazo", "atrasada", "nao_entregue"])
    a = p.parse_args()
    extras = {k: v for k, v in {"categoria": a.categoria, "entrega": a.entrega}.items() if v}
    imprimir(responder(a.pergunta, filtros_extras=extras or None))


if __name__ == "__main__":
    main()
