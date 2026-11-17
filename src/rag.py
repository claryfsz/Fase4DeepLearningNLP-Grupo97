"""Pipeline RAG completo (parte da L): pergunta -> evidências -> contexto -> Claude.

Fluxo:
    pergunta -> buscar_evidencias (embeddings + Chroma, src/retrieval.py)
             -> construção do contexto numerado [1], [2], ...
             -> geração com a API do Claude, restrita às evidências
             -> resposta + evidências citadas (rastreabilidade)

Duas camadas contra resposta sem base nos dados:
1. Código: status "sem_evidencia" (pergunta fora do escopo) não chama o LLM.
2. Prompt: o modelo deve responder "SEM_EVIDENCIA" quando as avaliações
   recuperadas não tratam da pergunta (ex.: "problemas da economia brasileira").

Uso:
    from src.rag import responder
    r = responder("Quais reclamações de entrega aparecem com maior frequência?")
    r["resposta"], r["evidencias_citadas"], r["status"]
"""
import os
import re

from src.retrieval import buscar_evidencias

try:  # .env é opcional; a chave também pode vir do ambiente
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:  # pragma: no cover
    pass

MODELO = os.getenv("CLAUDE_MODEL", "claude-sonnet-5-5")
MAX_TOKENS = 900
MARCADOR_RECUSA = "SEM_EVIDENCIA"

MSG_SEM_EVIDENCIA = (
    "Não encontrei avaliações na base que sustentem uma resposta para essa pergunta. "
    "A base contém avaliações de clientes de e-commerce (Olist, 2016-2018); "
    "tente perguntar sobre entrega, qualidade dos produtos, atendimento, "
    "elogios ou reclamações."
)

SYSTEM_PROMPT = f"""Você é um analista de Voice of Customer. Responde perguntas de gestores \
usando EXCLUSIVAMENTE as avaliações de clientes fornecidas no contexto.

Regras:
1. Use somente o que está nas avaliações. Não use conhecimento externo nem suponha causas.
2. Cite as evidências com o número entre colchetes, ex.: [3]. Toda afirmação relevante precisa \
de pelo menos uma citação.
3. Agrupe os achados por tema e destaque padrões recorrentes. Cada avaliação tem um campo \
"aparece N vezes": use-o como indício de volume ("relato repetido em N avaliações"). \
Não invente contagens, percentuais ou ranking de frequência que o contexto não permita.
4. Se as avaliações não tratarem da pergunta, ou forem insuficientes para responder com segurança, \
responda apenas com a palavra {MARCADOR_RECUSA} na primeira linha, seguida de uma frase curta \
dizendo o que falta. Não tente responder assim mesmo.
5. Se houver poucas evidências, diga isso explicitamente e evite generalizar.
6. Responda em português, de forma objetiva (até ~200 palavras), sem repetir as avaliações inteiras."""


# ------------------------------------------------------------------ contexto
def construir_contexto(evidencias: list[dict]) -> str:
    """Numera as evidências para que o modelo possa citá-las como [n]."""
    linhas = []
    for i, e in enumerate(evidencias, 1):
        volume = f" | aparece {e['n_duplicatas']} vezes" if e.get("n_duplicatas", 1) > 1 else ""
        linhas.append(
            f"[{i}] nota {e['score']} | {e['categoria']} | entrega {e['entrega']}{volume}\n"
            f"    \"{e['texto']}\""
        )
    return "\n".join(linhas)


def montar_mensagem_usuario(pergunta: str, evidencias: list[dict], status: str) -> str:
    aviso = ""
    if status == "evidencia_insuficiente":
        aviso = ("\nATENÇÃO: foram recuperadas poucas avaliações relevantes. "
                 "Deixe claro que a evidência é limitada.\n")
    return (f"Pergunta: {pergunta}\n{aviso}\n"
            f"Avaliações recuperadas ({len(evidencias)}):\n{construir_contexto(evidencias)}")


def extrair_citacoes(texto: str, n_evidencias: int) -> list[int]:
    """Números [n] realmente citados na resposta (ignora números fora do contexto)."""
    citados = {int(n) for grupo in re.findall(r"\[([\d,\s]+)\]", texto)
               for n in re.findall(r"\d+", grupo)}
    return sorted(n for n in citados if 1 <= n <= n_evidencias)


# --------------------------------------------------------------------- LLM
def _cliente():
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise SystemExit(
            "\n[erro] ANTHROPIC_API_KEY não definida.\n"
            "Copie .env.example para .env e preencha a chave (console.anthropic.com),\n"
            "ou exporte a variável no terminal.\n"
        )
    import anthropic
    return anthropic.Anthropic()


def gerar_resposta(pergunta: str, evidencias: list[dict], status: str, cliente=None) -> str:
    cliente = cliente or _cliente()
    msg = cliente.messages.create(
        model=MODELO,
        max_tokens=MAX_TOKENS,
        temperature=0,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": montar_mensagem_usuario(pergunta, evidencias, status)}],
    )
    return "".join(b.text for b in msg.content if getattr(b, "type", "") == "text").strip()


# --------------------------------------------------------------- pipeline
def responder(pergunta: str, cliente=None, **opcoes_busca) -> dict:
    """Contrato combinado com a MC: {"resposta", "evidencias", "status"} + extras.

    status: "ok" | "evidencia_insuficiente" | "sem_evidencia"
    `opcoes_busca` repassa filtros à recuperação (ex.: filtros_extras={"entrega": "atrasada"}).
    """
    busca = buscar_evidencias(pergunta, **opcoes_busca)
    base = {
        "pergunta": pergunta,
        "similaridade_pergunta": busca["similaridade_pergunta"],
        "intencao": busca["intencao"],
        "temas": busca["temas"],
        "consultas": busca["consultas"],
        "filtro": busca["filtro"],
    }

    # Camada 1: fora do escopo -> nem chama o LLM
    if busca["status"] == "sem_evidencia":
        return {**base, "status": "sem_evidencia", "resposta": MSG_SEM_EVIDENCIA,
                "evidencias": [], "evidencias_citadas": []}

    evidencias = busca["evidencias"]
    texto = gerar_resposta(pergunta, evidencias, busca["status"], cliente)

    # Camada 2: o próprio modelo recusou por falta de aderência
    if texto.upper().startswith(MARCADOR_RECUSA):
        motivo = texto[len(MARCADOR_RECUSA):].lstrip(" :.-\n")
        resposta = MSG_SEM_EVIDENCIA + (f"\n\nMotivo: {motivo}" if motivo else "")
        return {**base, "status": "sem_evidencia", "resposta": resposta,
                "evidencias": [], "evidencias_citadas": []}

    citadas = [evidencias[n - 1] for n in extrair_citacoes(texto, len(evidencias))]
    return {**base, "status": busca["status"], "resposta": texto,
            "evidencias": evidencias, "evidencias_citadas": citadas}
