"""Roda um conjunto de perguntas e salva as respostas em docs/exemplos_perguntas_respostas.md.

Uso (com a base indexada e ANTHROPIC_API_KEY definida):
    python -m scripts.gerar_exemplos
"""
from pathlib import Path

from src.rag import MODELO, responder

PERGUNTAS = [
    "Quais são os principais problemas relatados pelos clientes?",
    "Quais reclamações relacionadas à entrega aparecem com maior frequência?",
    "O que os clientes mais elogiam em suas experiências de compra?",
    "Quais problemas são relatados por clientes insatisfeitos?",
    "Existem padrões recorrentes nas avaliações relacionadas à qualidade dos produtos?",
    "Quais avaliações sustentam a conclusão de que existem problemas recorrentes relacionados ao prazo de entrega?",
    # sem evidência suficiente / fora do escopo
    "Qual é a capital da França?",
    "Quais são os principais problemas da economia brasileira?",
    # passa do limiar (0,862), mas a base não responde: 2ª camada, recusa do modelo
    "Quais problemas os clientes relatam ao pagar com Pix?",
]
SAIDA = Path(__file__).resolve().parents[1] / "docs" / "exemplos_perguntas_respostas.md"


def main():
    linhas = ["# Exemplos de perguntas e respostas", "",
              f"Gerado por `python -m scripts.gerar_exemplos` (modelo: `{MODELO}`).", ""]
    for i, pergunta in enumerate(PERGUNTAS, 1):
        print(f"[{i}/{len(PERGUNTAS)}] {pergunta}")
        r = responder(pergunta)
        linhas += [f"## {i}. {pergunta}", "",
                   f"- **Status:** `{r['status']}` | similaridade da pergunta: {r['similaridade_pergunta']} "
                   f"| intenção: {r['intencao']} | subconsultas: {len(r['consultas']) - 1}", "",
                   "**Resposta:**", "", r["resposta"], ""]
        if r["evidencias_citadas"]:
            linhas += ["**Evidências citadas:**", ""]
            for e in r["evidencias_citadas"]:
                linhas.append(f"- **[{e['ref']}]** `{e['review_id'][:8]}` · nota {e['score']} · {e['categoria']} · "
                              f"entrega {e['entrega']} · aparece {e['n_duplicatas']}x: \"{e['texto']}\"")
            linhas.append("")
    SAIDA.write_text("\n".join(linhas), encoding="utf-8")
    print(f"Salvo em {SAIDA}")


if __name__ == "__main__":
    main()
