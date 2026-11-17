"""Interface de demonstração (Streamlit): pergunta, resposta e evidências lado a lado.

Uso:  streamlit run app.py
"""
import streamlit as st

from src.rag import responder

st.set_page_config(page_title="Voice of Customer RAG", layout="wide")
st.title("Voice of Customer Intelligence")
st.caption("Pergunte em linguagem natural sobre as avaliações de clientes (Olist, 2016-2018).")

EXEMPLOS = [
    "Quais são os principais problemas relatados pelos clientes?",
    "Quais reclamações relacionadas à entrega aparecem com maior frequência?",
    "O que os clientes mais elogiam em suas experiências de compra?",
    "Qual é a capital da França?",
]
with st.sidebar:
    st.subheader("Filtros (opcional)")
    entrega = st.selectbox("Situação da entrega", ["(todas)", "no_prazo", "atrasada", "nao_entregue"])
    categoria = st.text_input("Categoria (ex.: beleza saude)")
    st.subheader("Exemplos")
    exemplo = st.radio("Escolha para preencher", ["(nenhum)"] + EXEMPLOS)

pergunta = st.text_input("Sua pergunta", value="" if exemplo == "(nenhum)" else exemplo)

if st.button("Perguntar", type="primary") and pergunta.strip():
    extras = {}
    if entrega != "(todas)":
        extras["entrega"] = entrega
    if categoria.strip():
        extras["categoria"] = categoria.strip()
    with st.spinner("Recuperando evidências e gerando a resposta..."):
        r = responder(pergunta, filtros_extras=extras or None)

    esq, dir_ = st.columns([3, 2])
    with esq:
        st.subheader("Resposta")
        (st.warning if r["status"] != "ok" else st.success)(f"Status: {r['status']}")
        st.write(r["resposta"])
        with st.expander("Como a busca foi feita"):
            st.write(f"Intenção: **{r['intencao']}** | temas: {r['temas'] or '-'} | "
                     f"similaridade da pergunta: {r['similaridade_pergunta']}")
            st.write("Consultas:", r["consultas"])
            st.write("Filtro:", r["filtro"])
    with dir_:
        st.subheader(f"Evidências citadas ({len(r['evidencias_citadas'])})")
        for e in r["evidencias_citadas"]:
            st.markdown(f"**[{e['ref']}] nota {e['score']}** · {e['categoria']} · entrega {e['entrega']} · "
                        f"aparece {e['n_duplicatas']}x · `{e['review_id'][:8]}`\n\n> {e['texto']}")
