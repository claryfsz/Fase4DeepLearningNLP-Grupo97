# Contrato entre a base de conhecimento (Maria Clara) e o pipeline RAG (Luiz Eduardo)

## O que a base de conhecimento entrega (Maria Clara)

Uma coleção ChromaDB persistida em `data/chroma`, chamada `avaliacoes_olist`
(constantes `config.CHROMA_DIR` e `config.COLLECTION_NAME`), com distância cosseno.

Cada documento tem:

- `id` = `review_id`
- `document` = texto limpo da avaliação (`"título. comentário"`)
- `metadata` = `review_id`, `order_id`, `score` (int), `data` (`YYYY-MM-DD`), `ano_mes`,
  `categoria`, `entrega` (`no_prazo` | `atrasada` | `nao_entregue`), `dias_atraso`
  (int, só quando houve entrega), `status_pedido`, `n_duplicatas` (int), `tem_titulo` (bool)

## Como o pipeline consulta a base (recomendado): `buscar_evidencias`

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
  `status="sem_evidencia"` sem nenhuma evidência. Nesse caso o pipeline **não chama o LLM**
  e responde que não há informação na base.

Parâmetros úteis:

- `filtros_extras={"categoria": "beleza saude"}` ou `{"entrega": "atrasada"}`
- `subconsultas=[...]`: para o pipeline passar subconsultas geradas pelo próprio LLM, no lugar do dicionário
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

## O que o pipeline entrega (Luiz Eduardo)

A função `responder(pergunta)`, em `src/rag.py`, recebe a pergunta, chama
`buscar_evidencias`, monta o contexto, gera a resposta com o Claude e devolve um dicionário.
É o ponto de entrada usado pela interface (`app.py`) e pelos scripts.

```python
from src.rag import responder

r = responder("Quais reclamações relacionadas à entrega aparecem com maior frequência?")
r = responder("O que os clientes elogiam?", filtros_extras={"categoria": "beleza saude"})
```

Parâmetros: além da pergunta, aceita os mesmos parâmetros de `buscar_evidencias`
(`filtros_extras`, `k_final`, `subconsultas`...), que são repassados à recuperação. O
parâmetro `cliente` permite injetar um cliente da API, útil para testes.

### Retorno

| Campo | Tipo | Conteúdo |
|---|---|---|
| `resposta` | str | Texto gerado, com as citações no formato `[n]`. Em caso de recusa, a mensagem padrão de falta de evidência |
| `status` | str | `ok`, `evidencia_insuficiente` ou `sem_evidencia` (ver tabela abaixo) |
| `evidencias` | list[dict] | Todas as avaliações enviadas ao modelo, na ordem numerada do contexto |
| `evidencias_citadas` | list[dict] | Só as avaliações que o modelo citou, cada uma com o campo `ref` (o número `[n]` usado no texto) |
| `pergunta` | str | A pergunta original |
| `similaridade_pergunta`, `intencao`, `temas`, `consultas`, `filtro` | — | Repassados de `buscar_evidencias`, para mostrar na demonstração como a busca foi feita |

### Status

| Status | Quando acontece | O LLM é chamado? | `evidencias` |
|---|---|---|---|
| `ok` | A busca encontrou 3 ou mais evidências e o modelo respondeu | Sim | Preenchida |
| `evidencia_insuficiente` | A busca encontrou só 1 ou 2 evidências | Sim, com um aviso no prompt para deixar a limitação clara | Preenchida |
| `sem_evidencia` (camada 1) | A pergunta ficou abaixo do limiar de 0,85 | Não | Vazia |
| `sem_evidencia` (camada 2) | O modelo respondeu `SEM_EVIDENCIA` porque as avaliações não tratam da pergunta. A resposta traz o motivo dado pelo modelo | Sim | Vazia |

### Como a resposta é gerada

1. **Contexto:** cada evidência vira uma linha numerada `[n]` com nota, categoria, situação
   da entrega e, quando o texto se repete na base, "aparece N vezes" (`n_duplicatas`).
2. **Prompt de sistema:** o modelo deve:
    - usar só as avaliações do contexto;
    - citar cada afirmação com `[n]`, e citar só avaliações que sustentam o que diz;
    - agrupar por tema e usar o "aparece N vezes" como indício de volume, sem inventar
      contagens, percentuais ou ranking;
    - responder `SEM_EVIDENCIA` quando as avaliações não tratam da pergunta;
    - escrever em português, com no máximo 180 palavras, 4 temas e 3 citações por tema.
3. **Rastreabilidade:** o código extrai os `[n]` da resposta, descarta números que não
   existem no contexto e monta `evidencias_citadas`. Toda evidência exibida existe de fato
   na base.

### Configuração

| Variável (arquivo `.env`) | Obrigatória | Uso |
|---|---|---|
| `ANTHROPIC_API_KEY` | Sim | Chave da API do Claude. Sem ela, o pipeline para com uma mensagem explicando como configurar |
| `CLAUDE_MODEL` | Não | Modelo usado na geração (padrão: `claude-sonnet-5-5`) |

O `.env` não é versionado. O repositório traz um `.env.example` como modelo.

### Onde o pipeline é usado

| Ponto de entrada | Comando |
|---|---|
| Interface com resposta e evidências lado a lado | `streamlit run app.py` |
| Pergunta pelo terminal | `python -m scripts.perguntar "sua pergunta"` |
| Gerar os exemplos do README | `python -m scripts.gerar_exemplos` |

## Avisos

- Textos genéricos ("Muito bom", "Recomendo") aparecem uma vez só. Use `n_duplicatas`
  para saber o volume real, por exemplo ao dizer "esse elogio aparece centenas de vezes".
- Para testar antes de a base completa ficar pronta, use
  `python -m src.build_index --amostra 500`.
