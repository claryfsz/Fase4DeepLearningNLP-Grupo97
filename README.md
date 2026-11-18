# Voice of Customer Intelligence com RAG

Tech Challenge · Fase 4 · Grupo 97 · PosTech

Solução RAG (Retrieval-Augmented Generation) que permite a gestores de e-commerce fazerem
perguntas em linguagem natural sobre as avaliações de clientes do
[Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
e receberem respostas **fundamentadas em avaliações reais**, com as evidências citadas.
Quando a base não tem informação suficiente, o sistema diz isso em vez de inventar.


## Arquitetura

```
Pergunta do usuário
   │
   ▼
Processamento da pergunta ── intenção (problema / elogio / neutra), tema, tipo (ampla ou específica)
   │
   ▼
Embeddings (multilingual-e5-small, prefixo "query: ")
   │
   ▼
Recuperação no ChromaDB ── filtro de nota por metadados + multi-query para perguntas amplas
   │                        + fusão por review_id + seleção em rodízio entre consultas
   │
   ├─ pergunta fora do escopo (similaridade < 0,85) ──▶ "sem evidência" (o LLM não é chamado)
   ▼
Construção do contexto ── avaliações numeradas [1], [2]... com nota, categoria, entrega e volume
   │
   ▼
Geração com Claude (API Anthropic) ── responde só com o contexto, cita [n], recusa se não houver base
   │
   ▼
Resposta + evidências citadas (review_id, texto, nota, categoria, entrega)
```

| Módulo | Função |
|---|---|
| `src/data_prep.py` | Seleção, limpeza e organização dos documentos (gera `documentos.parquet`) |
| `src/embeddings.py` | Embeddings de documentos (`passage:`) e perguntas (`query:`) |
| `src/build_index.py` | Indexação no ChromaDB |
| `src/retrieval.py` | Recuperação de evidências (`buscar_evidencias`) |
| `src/rag.py` | Pipeline completo (`responder`): contexto, geração e tratamento de falta de evidência |
| `app.py` | Interface de demonstração em Streamlit |
| `scripts/` | `perguntar.py` (terminal), `gerar_exemplos.py`, `testar_busca.py`, `testar_evidencias.py` |

## Tecnologias

| Componente | Escolha | Por quê |
|---|---|---|
| Linguagem / dados | Python, pandas, pyarrow | Preparação da base e formato colunar para os documentos |
| Embeddings | `intfloat/multilingual-e5-small` (sentence-transformers) | Multilíngue, treinado para recuperação, leve para rodar em CPU |
| Banco vetorial | ChromaDB (persistente, distância cosseno) | Sem servidor, guarda texto, vetor e metadados, filtra por metadados na busca |
| LLM | Claude (API Anthropic), modelo configurável por `CLAUDE_MODEL` | Segue bem instruções de fundamentação e recusa |
| Interface | Streamlit | Demonstração rápida: resposta e evidências lado a lado |

## Dados

O projeto usa o **[Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)**,
disponível no Kaggle: cerca de 100 mil pedidos feitos entre 2016 e 2018, com as avaliações
escritas pelos clientes.

Os arquivos de dados **não são versionados** neste repositório. O código fica no Git e os
dados ficam na fonte oficial, o que deixa a origem explícita e o histórico leve.

### Arquivos necessários

| Arquivo | Uso no projeto |
|---|---|
| `olist_order_reviews_dataset.csv` | Avaliações: nota, título e comentário. É a base de conhecimento. |
| `olist_orders_dataset.csv` | Datas de compra e de entrega, para o metadado de atraso |
| `olist_order_items_dataset.csv` | Liga cada pedido aos seus produtos |
| `olist_products_dataset.csv` | Categoria de cada produto |

Os demais arquivos do dataset (clientes, vendedores, pagamentos, geolocalização e tradução
das categorias) não são usados.

### Como obter

1. Acesse o [dataset no Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce).
   É preciso fazer login, e a conta é gratuita.
2. Clique em **Download** e descompacte o `.zip`.
3. Copie os 4 arquivos da tabela acima para a pasta `data/raw/` do projeto:

```
data/
└── raw/
    ├── olist_order_reviews_dataset.csv
    ├── olist_orders_dataset.csv
    ├── olist_order_items_dataset.csv
    └── olist_products_dataset.csv
```

Se algum arquivo estiver faltando, `python -m src.data_prep` para e informa quais são e
onde baixá-los.

### Licença

O dataset é publicado pela Olist no Kaggle sob a licença indicada na página do dataset.
Este projeto o utiliza apenas para fins acadêmicos.



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


## Pipeline RAG (geração)

A função `responder(pergunta)` em `src/rag.py` segue o contrato combinado entre a base e o
pipeline (`docs/contrato_base_pipeline.md`) e devolve `resposta`, `evidencias` e `status`, mais
`evidencias_citadas`, `intencao`, `consultas` e `similaridade_pergunta` para a demonstração.

1. **Recuperação:** `buscar_evidencias` (seção anterior) devolve até 30 avaliações.
2. **Construção do contexto:** cada avaliação vira uma entrada numerada, com nota, categoria,
   situação da entrega e, quando o texto se repete, "aparece N vezes". Esse campo é o único
   indício de volume que o modelo recebe.
3. **Geração:** o Claude recebe a pergunta, o contexto e um prompt de
   sistema que o obriga a usar só o contexto, citar `[n]`, não inventar contagens ou
   percentuais e recusar quando as avaliações não tratam da pergunta.
4. **Rastreabilidade:** o código extrai os `[n]` realmente citados e devolve só essas
   avaliações como `evidencias_citadas`. Números fora do contexto são ignorados.

### Perguntas sem evidência suficiente

Há duas camadas, porque a margem de similaridade entre "fora do escopo" e "pergunta ampla"
é estreita (veja as limitações acima):

| Situação | Tratamento | LLM chamado? |
|---|---|---|
| Pergunta fora do escopo (similaridade < 0,85) | `status = "sem_evidencia"` e mensagem padrão | Não |
| Poucas avaliações relevantes (< 3) | `status = "evidencia_insuficiente"`; o prompt pede que a limitação seja dita | Sim |
| Avaliações recuperadas não tratam da pergunta | O modelo responde `SEM_EVIDENCIA`; o código converte em `status = "sem_evidencia"` | Sim |

## Como executar

```bash
# 1. ambiente
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2. chave da API do Claude
cp .env.example .env          # edite e coloque a sua ANTHROPIC_API_KEY

# 3. dados: baixe os 4 CSVs do Kaggle para data/raw/ (veja a seção "Dados")

# 4. base de conhecimento
python -m src.data_prep
python -m src.build_index                  # ~7 min em CPU; ou: --amostra 5000 para testar

# 5. usar
python -m scripts.perguntar "Quais reclamações de entrega aparecem com maior frequência?"
streamlit run app.py                       # interface de demonstração
python -m scripts.gerar_exemplos           # regenera docs/exemplos_perguntas_respostas.md
```

Requisitos: Python 3.10+ e uma chave da API da Anthropic. No Windows, se o Chroma falhar ao
abrir o índice, defina `VOC_CHROMA_DIR` com um caminho simples sem acentos (ex.: `C:\chroma_voc`).

## Exemplos de perguntas e respostas

Respostas reais geradas pelo pipeline, com as evidências citadas, em
[`docs/exemplos_perguntas_respostas.md`](docs/exemplos_perguntas_respostas.md). O conjunto inclui
perguntas amplas, sobre um tema (entrega, qualidade), sobre elogios, sobre insatisfeitos, uma
pergunta que pede as evidências e duas sem base nos dados (*capital da França* e *economia
brasileira*).

## Principais decisões técnicas

| Decisão | Motivo |
|---|---|
| Um documento por avaliação, sem chunking | Avaliações são curtas (mediana de 62 caracteres) e cada uma é uma unidade citável |
| Agrupar textos idênticos e guardar `n_duplicatas` | Evita que "Muito bom" (371 cópias) ocupe o top-k, sem perder a noção de volume |
| Filtro de nota por intenção da pergunta | Faz perguntas sobre problemas recuperarem só avaliações de nota ≤ 2 |
| Multi-query + seleção em rodízio | Perguntas amplas recuperam pelas palavras; subconsultas concretas elevam a similaridade de ~0,87 para 0,94 a 0,97 e garantem cobertura de todos os temas |
| Limiar de escopo de 0,85 calibrado com testes | Separa perguntas fora do escopo (0,812 a 0,849) das amplas (0,861 ou mais) |
| Duas camadas contra resposta sem base | O limiar sozinho tem margem estreita; o prompt cobre os casos que passam por ele |
| Citações numeradas validadas em código | Garante que toda evidência exibida existe no contexto enviado ao modelo |


## Limitações

- O limiar de escopo tem margem estreita (0,849 fora do escopo × 0,861 na pergunta válida mais fraca) e depende de palavras-chave de intenção e de tema.
- O rodízio entre temas não mede frequência: o volume só aparece por `n_duplicatas`.
- Só 36,8% das avaliações têm texto; o restante tem apenas nota e não entra na base.
- A nota 3 fica fora dos filtros de problema e elogio por ser ambígua.
- Os metadados (nota, entrega, categoria) são usados nos filtros; filtro por período está
  disponível em `buscar_evidencias` (`filtros_extras={"ano_mes": "2018-03"}`), mas não na interface.

## Estrutura do repositório

```
├── app.py                  # demonstração (Streamlit)
├── src/                    # código-fonte (data_prep, embeddings, build_index, retrieval, rag)
├── scripts/                # utilitários de linha de comando
├── docs/                   # contrato, relatório da base, exemplos de perguntas e respostas
├── data/raw/               # CSVs do Kaggle (não versionados)
├── .env.example            # modelo do arquivo de chave da API
└── requirements.txt
```
## Integrantes

Maria Clara Ferreira RM: 371497
Luiz Eduardo Oliveira RM: 374244