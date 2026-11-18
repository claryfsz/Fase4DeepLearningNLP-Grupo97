# Base de conhecimento (seção do README, parte da Maria Clara)

> Texto pronto para colar no README.md. Os números vêm de `docs/relatorio_base.md`,
> gerado por `python -m src.data_prep`.

## Preparação da base

### Seleção dos dados

A fonte principal é `olist_order_reviews_dataset.csv` (99.224 avaliações), porque o
desafio trata do conteúdo textual das avaliações. Para enriquecer cada documento com
contexto, juntamos também `olist_orders_dataset.csv` (datas de entrega),
`olist_order_items_dataset.csv` e `olist_products_dataset.csv` (categoria do produto).
Clientes, vendedores, pagamentos, geolocalização e tradução das categorias não entraram porque não acrescentam
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

Tempo de indexação na nossa máquina (CPU, sem GPU): **7 min 28 s** para os 36.510 documentos, cerca de 80 documentos por segundo. A maior parte desse tempo é a geração dos embeddings. Para iterar mais rápido durante o desenvolvimento, use `--amostra 5000`.

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

## Estratégia de recuperação

A recuperação fica em `src/retrieval.py`, na função `buscar_evidencias(pergunta)`. Cada
decisão abaixo veio de um teste com a base completa (36.510 documentos), comparando com a
versão anterior.

### 1. Problema: perguntas amplas recuperam pelas palavras, não pelo sentido

Busca simples (top-5, sem filtro) para *"Quais são os principais problemas relatados
pelos clientes?"*:

- similaridade do 1º resultado de apenas **0,878**;
- o 1º resultado foi *"Problemas com os Correios"*, com **nota 5**, que bateu só pela
  palavra "problemas";
- outros resultados bateram pela palavra "cliente" (*"Sou cliente há anos..."*).

Isso acontece porque a pergunta é abstrata e as avaliações são curtas e concretas. O
modelo acaba se apoiando nas palavras em comum.

### 2. Filtro de nota pelos metadados

A função detecta a intenção da pergunta por palavras-chave:

| Intenção | Exemplo | Filtro aplicado |
|---|---|---|
| Problema | "reclamações", "insatisfeitos", "defeito" | `score <= 2` |
| Elogio | "elogiam", "recomendam", "satisfeitos" | `score >= 4` |
| Neutra | demais perguntas | nenhum |

Com top-30 e filtro `nota <= 2`, todas as 30 evidências passaram a ser reclamações reais.
Mas a similaridade continuou baixa (0,864 a 0,877) e o viés das palavras permaneceu: vieram
muitos "resolva meu problema" e nenhuma reclamação de produto com defeito.

A nota 3 fica fora dos dois filtros por ser ambígua: mistura elogio e crítica no mesmo
texto.

### 3. Multi-query: expandir a pergunta em buscas concretas

Perguntas amplas ("principais", "quais", "padrões", "mais frequentes") são expandidas em
subconsultas concretas, organizadas em 5 temas: entrega, qualidade, atendimento, pedido
errado/incompleto e financeiro. Exemplos de subconsultas: *"produto chegou quebrado"*,
*"não consigo contato com a loja, ninguém responde"*, *"cancelei a compra e não recebi o
estorno"*.

- Se a pergunta cita um tema ("problemas de **entrega**"), usa só as subconsultas desse
  tema.
- Perguntas específicas ("produto chegou quebrado") não são expandidas, porque já atingem
  ~0,96.
- O parâmetro `subconsultas` permite trocar o dicionário por subconsultas geradas pelo LLM.

Resultado: a similaridade das evidências subiu de **~0,87 para 0,94 a 0,97**.

### 4. Seleção em rodízio entre as consultas

A primeira versão juntava os resultados de todas as subconsultas e cortava os 30 mais
similares. O teste mostrou que esse corte global **eliminava temas inteiros**:

| Pergunta | Corte global | Rodízio |
|---|---|---|
| Principais problemas | atendimento e financeiro com **0** evidências | **11 de 11** consultas, 2 a 3 evidências cada |
| O que mais elogiam | atendimento com **0** evidências | **9 de 9** consultas, 3 a 4 evidências cada |

A causa: avaliações curtas e literais (*"Produto não entregue"*, 0,96) vencem relatos mais
longos sobre atendimento (~0,93). Mas "atendimento que não responde" era justamente a
reclamação mais frequente na busca simples.

No rodízio, cada consulta contribui com seu melhor resultado, depois com o segundo melhor,
e assim por diante até completar `k_final = 30`. Avaliações encontradas por mais de uma
consulta aparecem uma vez só, com o campo `encontrada_por` listando as consultas.

### 5. Detecção de perguntas fora do escopo

O modelo e5 dá similaridades altas mesmo para textos sem relação, então o limiar foi
calibrado com testes reais:

| Tipo de pergunta | Similaridade do 1º resultado |
|---|---|
| Fora do escopo (*"qual a capital da França?"*) | 0,812 a 0,836 |
| Fora do escopo com palavras da base (*"principais problemas da economia brasileira?"*) | 0,849 |
| Ampla (*"clientes insatisfeitos"*, *"principais problemas"*, *"o que mais elogiam"*) | 0,861 a 0,892 |
| Específica (*"produto chegou quebrado"*) | 0,95 a 0,97 |

**Limiar de escopo: 0,85.** O limiar é aplicado só à **pergunta original**, nunca às
subconsultas, que sempre encontram algo. Abaixo dele, a função devolve
`status = "sem_evidencia"` sem nenhuma avaliação, e o LLM não é chamado.

Um caso curioso: para "capital da França", a busca devolveu avaliações sobre **capinha** de
celular. Sem nada relevante na base, o modelo se apegou à semelhança da palavra. Esse é o
motivo de não mandar o top-k direto para o LLM sem um critério de corte.

Também são descartadas evidências individuais com similaridade abaixo de 0,85. Se sobrarem
menos de 3, o status é `evidencia_insuficiente`.

### Limitações conhecidas

- **Margem estreita:** só ~0,012 separa a pergunta fora do escopo mais alta (*"economia
  brasileira"*, 0,849) da pergunta ampla mais fraca (*"clientes insatisfeitos"*, 0,861). A
  pergunta sobre economia foi barrada por apenas 0,0006 abaixo do limiar: perguntas fora do
  escopo que usam palavras da base podem passar. Por isso existe uma segunda camada no
  prompt: o LLM é instruído a recusar quando as evidências não tratam da pergunta.
- **O rodízio não mede frequência:** como cada tema recebe uma cota parecida, o número de
  evidências por tema não indica qual problema é mais comum. O indício de volume está no
  campo `n_duplicatas` (ex.: *"Produto não entregue"* aparece 13 vezes).
- **Intenção por palavras-chave:** é simples e transparente, mas pode errar em perguntas
  com negação ou ironia.
- **Lojas anonimizadas:** nomes como "lannister" e "stark" nos textos são a anonimização
  dos vendedores feita pela própria Olist, não um erro de dado.
