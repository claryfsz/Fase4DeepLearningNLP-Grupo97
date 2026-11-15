# Contrato entre a base (MC) e o pipeline (L)

## O que a MC entrega

Uma coleção ChromaDB persistida em `data/chroma`, chamada `avaliacoes_olist`
(constantes `config.CHROMA_DIR` e `config.COLLECTION_NAME`), com distância cosseno.

Cada documento tem:

- `id` = `review_id`
- `document` = texto limpo da avaliação (`"título. comentário"`)
- `metadata` = `review_id`, `order_id`, `score` (int), `data` (`YYYY-MM-DD`), `ano_mes`,
  `categoria`, `entrega` (`no_prazo` | `atrasada` | `nao_entregue`), `dias_atraso`
  (int, só quando houve entrega), `status_pedido`, `n_duplicatas` (int), `tem_titulo` (bool)

## Como a L consulta (recomendado): `buscar_evidencias`

```python
from src.retrieval import buscar_evidencias

r = buscar_evidencias("Quais são os principais problemas relatados pelos clientes?")
r["status"]                 # "ok" | "evidencia_insuficiente" | "sem_evidencia"
r["evidencias"]             # lista de dicts: review_id, texto, similaridade, score,
                            # categoria, entrega, data, n_duplicatas, encontrada_por
r["similaridade_pergunta"]  # top-1 da pergunta original (decide o escopo)
r["intencao"], r["temas"], r["consultas"], r["filtro"]   # para mostrar na demo
```

O que ela já faz:

- **Filtro de nota automático:** perguntas sobre problemas buscam nota ≤ 2, sobre elogios nota ≥ 4.
- **Multi-query:** perguntas amplas viram subconsultas concretas por tema (entrega,
  qualidade, atendimento, pedido errado, financeiro). Específicas não são expandidas.
- **Fusão:** junta os resultados por `review_id` e descarta similaridade < 0,85.
- **Fora do escopo:** se a pergunta original fica abaixo de 0,85, devolve
  `status="sem_evidencia"` sem nenhuma evidência. Nesse caso a L **não chama o LLM**
  e responde que não há informação na base.

Parâmetros úteis:

- `filtros_extras={"categoria": "beleza saude"}` ou `{"entrega": "atrasada"}`
- `subconsultas=[...]`: para a L passar subconsultas geradas pelo próprio LLM, no lugar do dicionário
- `k_final=30`: máximo de evidências enviadas ao prompt

Limitação conhecida: uma pergunta fora do escopo que use palavras da base
("principais problemas da economia brasileira") pode passar do limiar. Por isso o
prompt também precisa mandar o LLM recusar quando as evidências não tratam da pergunta.

Para ver o que a função faz com uma pergunta, sem LLM:
`python -m scripts.testar_evidencias "sua pergunta"`

## Consulta direta ao Chroma (se precisar)

```python
import chromadb
from src import config
from src.embeddings import embed_query   # NUNCA chamar o modelo direto (prefixo "query:")

colecao = chromadb.PersistentClient(path=str(config.CHROMA_DIR)).get_collection(config.COLLECTION_NAME)
res = colecao.query(
    query_embeddings=[embed_query(pergunta)],
    n_results=10,
    where={"score": {"$lte": 2}},          # opcional
)
# similaridade = 1 - res["distances"][0][i]   (útil para o limiar de "sem evidência")
```

Exemplos de filtro:

- Insatisfeitos: `{"score": {"$lte": 2}}`
- Entregas atrasadas: `{"entrega": "atrasada"}`
- Categoria: `{"categoria": "beleza saude"}` (nomes com espaço no lugar de `_`)
- Período: `{"ano_mes": "2018-03"}`
- Combinado: `{"$and": [{"score": {"$lte": 2}}, {"entrega": "atrasada"}]}`

## O que a L entrega

`responder(pergunta) -> {"resposta": str, "evidencias": list[dict], "status": str}`

## Avisos

- Textos genéricos ("Muito bom", "Recomendo") aparecem uma vez só. Use `n_duplicatas`
  para saber o volume real, por exemplo ao dizer "esse elogio aparece centenas de vezes".
- Para testar antes de a base completa ficar pronta, use
  `python -m src.build_index --amostra 500`.
