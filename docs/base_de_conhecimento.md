# Base de conhecimento (seção do README, parte da MC)

> Texto pronto para colar no README.md. Os números vêm de `docs/relatorio_base.md`,
> gerado por `python -m src.data_prep`.

## Preparação da base

### Seleção dos dados

A fonte principal é `olist_order_reviews_dataset.csv` (99.224 avaliações), porque o
desafio trata do conteúdo textual das avaliações. Para enriquecer cada documento com
contexto, juntamos também `olist_orders_dataset.csv` (datas de entrega),
`olist_order_items_dataset.csv` e `olist_products_dataset.csv` (categoria do produto).
Clientes, vendedores, pagamentos e geolocalização não entraram porque não acrescentam
informação relevante para as perguntas sobre a voz do cliente.

### Tratamento de valores ausentes

| Campo | Ausentes | Decisão |
|---|---:|---|
| Título (`review_comment_title`) | 88,3% | Vira string vazia. O documento usa só o comentário. |
| Comentário (`review_comment_message`) | 58,7% | Vira string vazia. O documento usa só o título. |
| Título **e** comentário | 57,0% | Avaliação descartada, porque não tem texto para recuperar. |
| Categoria do produto | 999 documentos (2,7%) | Preenchida como `desconhecida`. |
| Data de entrega | pedidos não entregues | `entrega = nao_entregue` e sem `dias_atraso`. |

A maior parte das avaliações tem só a nota, sem texto. Por isso a base indexada fica
bem menor que a original (36.510 documentos, 36,8% do total).

### Limpeza dos textos

- Normalização Unicode (NFC), para que a mesma palavra acentuada tenha sempre a mesma
  representação.
- Remoção de quebras de linha (`\r\n`), tabs e espaços repetidos.
- Remoção de pontuação solta no início e no fim.
- Descarte de textos com menos de 3 caracteres (`"."`, `"ok"`), que não carregam informação.
- **Mantivemos** acentos, maiúsculas e stopwords, porque o modelo de embeddings é
  treinado com texto natural e usa esse contexto.

### Duplicatas

1. **`review_id` repetido** (814 casos): a mesma avaliação aparece ligada a mais de um
   pedido. Mantemos a primeira ocorrência.
2. **Textos idênticos com a mesma nota** (ex.: "Muito bom" aparece 371 vezes): mantemos um
   documento e guardamos a frequência em `n_duplicatas`. Sem isso, as cópias ocupariam
   todo o top-k e esconderiam avaliações diferentes. Com o campo, o pipeline ainda sabe
   quantas vezes aquele relato apareceu.

### Organização dos documentos

Cada avaliação vira um documento com o texto `"<título>. <comentário>"`. O título vem
primeiro porque costuma resumir a opinião ("Não recebi", "Recomendo"). Os documentos são
curtos (mediana de 62 caracteres, máximo de 229), então **não fazemos chunking**: uma
avaliação é uma unidade de evidência e pode ser citada inteira pelo `review_id`.

Metadados de cada documento:

| Campo | Exemplo | Uso |
|---|---|---|
| `review_id` | `7bc2406...` | Identificador da evidência citada na resposta |
| `order_id` | `73fc742...` | Rastreabilidade até o pedido |
| `score` | `1` a `5` | Filtrar insatisfeitos/satisfeitos |
| `data` / `ano_mes` | `2018-01-18` / `2018-01` | Filtro por período |
| `categoria` | `cama mesa banho` | Filtro por categoria (mais frequente do pedido) |
| `entrega` | `no_prazo`, `atrasada`, `nao_entregue` | Comparar entrega real × prevista |
| `dias_atraso` | `8` | Quantos dias depois do prazo estimado (negativo = adiantado) |
| `status_pedido` | `delivered` | Status do pedido |
| `n_duplicatas` | `371` | Quantas vezes esse texto apareceu com essa nota |

## Embeddings

Modelo: **`intfloat/multilingual-e5-small`** (384 dimensões).

- **Multilíngue:** as avaliações estão em português, e modelos só em inglês perdem muito
  significado.
- **Treinado para recuperação:** a família E5 foi treinada com pares pergunta → passagem,
  o mesmo cenário do RAG. Modelos de paráfrase (como o `paraphrase-multilingual-MiniLM`)
  são treinados para medir semelhança entre frases.
- **Leve:** roda em CPU num tempo viável para cerca de 36 mil documentos curtos.
- Usa os prefixos `passage:` nos documentos e `query:` nas perguntas, como recomenda o
  modelo. As duas funções ficam em `src/embeddings.py` e são compartilhadas com o
  pipeline, o que garante que pergunta e base estejam no mesmo espaço vetorial.
- Vetores normalizados (norma 1), então a distância cosseno fica estável.

Os embeddings são gerados em lotes de 64 (`EMBEDDING_BATCH_SIZE`).

## Armazenamento e indexação

**ChromaDB** persistido em disco (`data/chroma`), coleção `avaliacoes_olist`,
índice HNSW com distância cosseno.

- Guarda texto, vetor e metadados juntos, então a evidência volta pronta para ser exibida.
- Permite filtrar por metadados na própria busca (`where={"score": {"$lte": 2}}`), sem
  pós-processamento.
- Não precisa de servidor: basta clonar o repo e rodar o script.
- O id de cada documento é o `review_id`, o que permite citar e auditar cada evidência.

Tempo de indexação na nossa máquina: **[preencher com a saída do `build_index`]**.

## Como reproduzir esta etapa

```bash
# 1. baixar os CSVs do Kaggle para data/raw/
#    https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
# 2. preparar a base (gera data/processed/documentos.parquet e docs/relatorio_base.md)
python -m src.data_prep
# 3. gerar embeddings e indexar (gera data/chroma/)
python -m src.build_index            # base completa
python -m src.build_index --amostra 5000   # alternativa rápida, estratificada por nota
# 4. testar a recuperação sem LLM
python -m scripts.testar_busca "produto chegou quebrado" --k 5 --nota-max 2
```
