# Exemplos de perguntas e respostas

Gerado por `python -m scripts.gerar_exemplos` (modelo: `claude-sonnet-5-5`).

## 1. Quais são os principais problemas relatados pelos clientes?

- **Status:** `ok` | similaridade da pergunta: 0.8672 | intenção: problema | subconsultas: 10

**Resposta:**

**Principais problemas relatados (30 avaliações recuperadas)**

1. **Produto não entregue ou atrasado**: é o tema com maior volume repetido. "Produto não entregue" aparece em 13 avaliações [3], outro relato semelhante em 6 [2] e "Atraso na entrega" em 6 [7]. Há também casos de compra cancelada por indisponibilidade do produto [25][27].

2. **Produto com defeito ou diferente do anunciado**: itens quebrados [1] (relato repetido em 2 avaliações) [5][6], produtos que não funcionam [12] (2 avaliações) [13] e produtos diferentes do anunciado [9][10][15].

3. **Pedido incompleto**: clientes receberam o pedido faltando itens [16][17][19]. Um cliente relata que só 1 produto foi entregue, embora constasse como entregue [30].

4. **Atendimento sem resposta e dificuldade de estorno**: clientes não obtêm retorno da loja [20][22][26]. Há reclamações de estorno não recebido [24] ou condicionado a ir a uma agência bancária [25].

**Ressalva:** a amostra é pequena e o campo "aparece N vezes" só indica repetição de cada relato. Não permite ranking exato nem percentuais.

**Evidências citadas:**

- **[1]** `43bf7d48` · nota 1 · telefonia · entrega no_prazo · aparece 2x: "O produto chegou quebrado"
- **[2]** `0ccfc62c` · nota 1 · bebes · entrega atrasada · aparece 6x: "Produto não foi entregue"
- **[3]** `7ff39d79` · nota 1 · cool stuff · entrega atrasada · aparece 13x: "Produto não entregue"
- **[5]** `03a673dc` · nota 2 · brinquedos · entrega no_prazo · aparece 1x: "Produto veio quebrado"
- **[6]** `1f9abf59` · nota 1 · brinquedos · entrega no_prazo · aparece 1x: "o produto veio quebrado"
- **[7]** `69528881` · nota 1 · papelaria · entrega atrasada · aparece 6x: "Atraso na entrega"
- **[9]** `b350f1b9` · nota 1 · informatica acessorios · entrega no_prazo · aparece 1x: "Recebi um produto diferente do anunciado"
- **[10]** `f85ae141` · nota 1 · automotivo · entrega no_prazo · aparece 1x: "O produto chegou diferente do anunciado"
- **[12]** `6d27bb9c` · nota 1 · informatica acessorios · entrega no_prazo · aparece 2x: "produto não funciona"
- **[13]** `a61e65fa` · nota 1 · automotivo · entrega no_prazo · aparece 1x: "Produto com defeito. Produto não funciona"
- **[15]** `51a15782` · nota 1 · informatica acessorios · entrega no_prazo · aparece 1x: "produto diferente do anunciado"
- **[16]** `ee36eb06` · nota 1 · pet shop · entrega no_prazo · aparece 1x: "Pedido entregue incompleto"
- **[17]** `0afdaef4` · nota 1 · beleza saude · entrega no_prazo · aparece 1x: "Recebi o produto incompleto, faltou 01 item!"
- **[19]** `d100adcd` · nota 2 · utilidades domesticas · entrega no_prazo · aparece 1x: "Pedido incompleto. Meu pedido chegou faltando um item"
- **[20]** `60d722b7` · nota 1 · brinquedos · entrega atrasada · aparece 1x: "Não recebi meu produto,e ja mandei mensagem pra loja mas ninguém me responde"
- **[22]** `47f083e5` · nota 1 · bebes · entrega atrasada · aparece 1x: "Produto não entregue e loja não deu satisfação após contato"
- **[24]** `a9761241` · nota 1 · moveis decoracao · entrega atrasada · aparece 1x: "Estou esperando meu estorno, a compra foi cancelada e não obtive nenhuma resposta é não recebi o estorno"
- **[25]** `b943aa9b` · nota 1 · consoles games · entrega nao_entregue · aparece 1x: "10 dias após efetuar a compra, gerar o boleto e pagar, recebo um e-mail cancelando a compra por falta do produto. Para o estorno do valor me obrigaram a ir em uma agência bancaria e retirar o valor!"
- **[26]** `7e46bb8d` · nota 1 · cama mesa banho · entrega atrasada · aparece 1x: "Compre ja tem dias e ate agora nao entregaram e nem me responde os meus contatos"
- **[27]** `d3b9ad72` · nota 1 · desconhecida · entrega nao_entregue · aparece 1x: "produto indisponivel"
- **[30]** `42a3a3e2` · nota 1 · cool stuff · entrega no_prazo · aparece 1x: "Em partes. Sou cliente há anos, porém sempre há divergências e problemas na entrega, consta como produto entregue, porém foi entregue apenas 1 produto, aguardo solução!"

## 2. Quais reclamações relacionadas à entrega aparecem com maior frequência?

- **Status:** `ok` | similaridade da pergunta: 0.8727 | intenção: problema | subconsultas: 4

**Resposta:**

**Reclamações de entrega mais recorrentes**

1. **Produto não entregue**: é o relato com maior repetição individual. [2] aparece 13 vezes e [1] aparece 6 vezes. Também há [5].

2. **Atraso e demora**: é o tema com mais avaliações distintas. Relatos repetidos: [20] (7 vezes), [7] (6 vezes) e [12] (5 vezes). Em [20], o cliente reclama de demora mesmo com a entrega marcada como "no_prazo".

3. **Rastreamento falho, com menção aos Correios**: o código não atualiza e o produto fica parado. Exemplos: [17], [22], [19]. Em [30], o cliente diz que não havia nenhuma informação no rastreio.

4. **Falta de retorno da loja**: clientes dizem que não receberam resposta ou detalhes sobre o pedido. Exemplos: [24], [25], [22].

**Ressalva:** os números de "aparece N vezes" indicam volume apenas nas avaliações que os trazem. Por isso não dá para montar um ranking exato entre os temas.

**Evidências citadas:**

- **[1]** `0ccfc62c` · nota 1 · bebes · entrega atrasada · aparece 6x: "Produto não foi entregue"
- **[2]** `7ff39d79` · nota 1 · cool stuff · entrega atrasada · aparece 13x: "Produto não entregue"
- **[5]** `a1cdd61d` · nota 1 · telefonia · entrega atrasada · aparece 1x: "Produto nao foi entregue"
- **[7]** `69528881` · nota 1 · papelaria · entrega atrasada · aparece 6x: "Atraso na entrega"
- **[12]** `bb2810db` · nota 1 · automotivo · entrega atrasada · aparece 5x: "Muita demora na entrega"
- **[17]** `22bdc97e` · nota 1 · informatica acessorios · entrega nao_entregue · aparece 1x: "produto entregue pelos correios que não atualizou status de rastreamento e nem entregou produto"
- **[19]** `3ee8556f` · nota 2 · esporte lazer · entrega no_prazo · aparece 1x: "Rastreio falho,produto ficou parado na postagem"
- **[20]** `97b1c66c` · nota 1 · cama mesa banho · entrega no_prazo · aparece 7x: "Demora na entrega"
- **[22]** `b7c1d885` · nota 1 · relogios presentes · entrega atrasada · aparece 1x: "Boa noite, não recebi o produto. Correios nunca atualizou o código de rastreio e nem uma posição da loja até o momento"
- **[24]** `209a90c3` · nota 1 · brinquedos · entrega nao_entregue · aparece 1x: "Procurei as agências do correio o produto não estava postado, não tive nenhuma resposta sobre o mesmo. Total insatisfação, aguardo resposta! Obs.: Pelo cód de rastreamento já está postado Mas n rece"
- **[25]** `d6a5ec07` · nota 1 · desconhecida · entrega nao_entregue · aparece 1x: "Total falta de respeito com o consumidor. Além de não realizar a entrega que tinha um prazo enorme, ao longo do período, pedi mais detalhes do status para acompanhar o processo e nunca ligaram"
- **[30]** `f36a27bd` · nota 1 · beleza saude · entrega atrasada · aparece 1x: "Estou muito descontente. Sempre comprei com vocês. Antes não tinha problema com a entrega. Desta vez além de não entregarem, eu nem sei o que aconteceu. Não tem nenhuma informação no rastreamento"

## 3. O que os clientes mais elogiam em suas experiências de compra?

- **Status:** `ok` | similaridade da pergunta: 0.8835 | intenção: elogio | subconsultas: 8

**Resposta:**

**Principais elogios**

1. **Entrega rápida e dentro do prazo**: é o tema mais presente. Há relatos de entrega antes do prazo [5][8][10], de chegada no prazo e bem embalada [2][3][4] e de loja com entrega rápida [24][26][27]. Também aparece em [29] ("muito antes do prazo").

2. **Qualidade do produto**: "Produto de ótima qualidade" aparece repetido em 16 avaliações [6] e em outras 3 [7]. "Produto de Boa Qualidade" aparece em 12 [20]. Também há elogios a material resistente [11][18][19]. Em volume, os campos "aparece N vezes" indicam que este é um tema forte.

3. **Custo-benefício**: elogiado como excelente [16][17] e como bom [15].

4. **Atendimento do vendedor e da loja**: elogios ao vendedor [21][23][25] e ao compromisso com o cliente [28][29].

**Ressalva**: produto entregue conforme o anunciado também é citado [12][13][14], mas em menor escala. Não é possível montar um ranking exato entre os temas, só indicar que qualidade tem os maiores volumes repetidos.

**Evidências citadas:**

- **[2]** `79a4f071` · nota 5 · esporte lazer · entrega no_prazo · aparece 1x: "chegou dentro do prazo e bem embalado"
- **[3]** `831a7717` · nota 5 · esporte lazer · entrega no_prazo · aparece 1x: "Produto chegou dentro do prazo e bem embalado"
- **[4]** `31185145` · nota 5 · moveis decoracao · entrega no_prazo · aparece 1x: "Dentro do prazo e bem embalado"
- **[5]** `c6d02e0d` · nota 5 · informatica acessorios · entrega no_prazo · aparece 1x: "entrega muito rápida, antes do prazo estipulado"
- **[6]** `34b941f9` · nota 5 · cama mesa banho · entrega no_prazo · aparece 16x: "Produto de ótima qualidade"
- **[7]** `7c80e9e0` · nota 4 · cama mesa banho · entrega no_prazo · aparece 3x: "Produto de ótima qualidade"
- **[8]** `ffee16b6` · nota 5 · ferramentas jardim · entrega no_prazo · aparece 1x: "Entrega rápida , muito antes do prazo"
- **[10]** `184aef5f` · nota 5 · esporte lazer · entrega no_prazo · aparece 1x: "Super rapida entrega chegou antes do prazo"
- **[11]** `0ac29099` · nota 5 · automotivo · entrega no_prazo · aparece 1x: "O produto excelente material resistente"
- **[12]** `7ede1fb0` · nota 4 · esporte lazer · entrega no_prazo · aparece 1x: "produto entregue conforme o anunciado"
- **[13]** `d44b85fd` · nota 4 · cama mesa banho · entrega no_prazo · aparece 2x: "produto entregue conforme anunciado"
- **[14]** `96c909fa` · nota 5 · moveis decoracao · entrega no_prazo · aparece 1x: "lindo , produto igual ao anunciado"
- **[15]** `c82c423f` · nota 5 · fraldas higiene · entrega no_prazo · aparece 1x: "ótima qualidade,bom custo beneficio"
- **[16]** `edd265dc` · nota 5 · cool stuff · entrega no_prazo · aparece 1x: "Excelente custo beneficio, muito bonitinho"
- **[17]** `9fee00eb` · nota 5 · sinalizacao e seguranca · entrega no_prazo · aparece 1x: "Excelente custo beneficio"
- **[18]** `4ca66d8e` · nota 5 · utilidades domesticas · entrega no_prazo · aparece 1x: "Produto muito bom e com material resistente"
- **[19]** `9700a96c` · nota 4 · malas acessorios · entrega no_prazo · aparece 1x: "produto muito bom, com material resistente"
- **[20]** `29a2c76d` · nota 5 · beleza saude · entrega no_prazo · aparece 12x: "Produto de Boa Qualidade"
- **[21]** `37177254` · nota 5 · esporte lazer · entrega no_prazo · aparece 1x: "Muito boa a atenção do vendedor"
- **[23]** `c4b1a02b` · nota 5 · perfumaria · entrega no_prazo · aparece 1x: "Vendedor excelente"
- **[24]** `dfd91cc7` · nota 5 · eletronicos · entrega no_prazo · aparece 1x: "Ótima loja, a entrega é rápida recomendo"
- **[25]** `a9f0c655` · nota 5 · ferramentas jardim · entrega no_prazo · aparece 1x: "excelente vendedor"
- **[26]** `a5e060bd` · nota 5 · cool stuff · entrega no_prazo · aparece 1x: "otima loja entregua rapida"
- **[27]** `89108dc4` · nota 5 · cool stuff · entrega no_prazo · aparece 1x: "Recomendo a loja produto entregue rapido"
- **[28]** `11ad825a` · nota 5 · esporte lazer · entrega no_prazo · aparece 1x: "Perfeito!. Agilidade e compromisso com o cliente. Recomendo de olhos fechados. Parabéns!"
- **[29]** `3cc0bb49` · nota 5 · perfumaria · entrega no_prazo · aparece 1x: "Muito bom muito antes do prazo eu recebi a mercadoria. Breve comprarei mais produtos muito bom o comprometimento de vcs ao cliente. Meus parabéns!!"

## 4. Quais problemas são relatados por clientes insatisfeitos?

- **Status:** `ok` | similaridade da pergunta: 0.8608 | intenção: problema | subconsultas: 10

**Resposta:**

**Problemas relatados por clientes insatisfeitos (maioria nota 1)**

1. **Produto não entregue ou atrasado**
   - "Produto não entregue" aparece repetido em 13 avaliações [3].
   - "Produto não foi entregue", em 6 avaliações [2].
   - "Atraso na entrega", em 6 avaliações [7].

2. **Produto com problema ao chegar**
   - Chegou quebrado [1][5][6].
   - Não funciona ou veio com defeito [11][12][13].
   - Diferente do anunciado [9][10][15].
   - Pedido incompleto, com item faltando [16][17][19].

3. **Atendimento ausente ou ruim**
   - Clientes contataram a loja e não obtiveram resposta [20][22][26].
   - Há também queixas gerais de mau atendimento e falta de respeito [18][21][30].

4. **Cancelamento e estorno**
   - Compra cancelada por falta do produto [25][28].
   - Cancelamento sem explicação e sem canal de contato [29].
   - Estorno não recebido [24], ou exigência de ir a uma agência bancária para retirar o valor [25].

**Observação:** os temas 3 e 4 aparecem em poucas avaliações, sem indicação de repetição. Os campos de repetição só permitem apontar volume maior para não entrega e atraso.

**Evidências citadas:**

- **[1]** `43bf7d48` · nota 1 · telefonia · entrega no_prazo · aparece 2x: "O produto chegou quebrado"
- **[2]** `0ccfc62c` · nota 1 · bebes · entrega atrasada · aparece 6x: "Produto não foi entregue"
- **[3]** `7ff39d79` · nota 1 · cool stuff · entrega atrasada · aparece 13x: "Produto não entregue"
- **[5]** `03a673dc` · nota 2 · brinquedos · entrega no_prazo · aparece 1x: "Produto veio quebrado"
- **[6]** `1f9abf59` · nota 1 · brinquedos · entrega no_prazo · aparece 1x: "o produto veio quebrado"
- **[7]** `69528881` · nota 1 · papelaria · entrega atrasada · aparece 6x: "Atraso na entrega"
- **[9]** `b350f1b9` · nota 1 · informatica acessorios · entrega no_prazo · aparece 1x: "Recebi um produto diferente do anunciado"
- **[10]** `f85ae141` · nota 1 · automotivo · entrega no_prazo · aparece 1x: "O produto chegou diferente do anunciado"
- **[11]** `002d6d96` · nota 2 · automotivo · entrega no_prazo · aparece 1x: "Produto não funciona"
- **[12]** `6d27bb9c` · nota 1 · informatica acessorios · entrega no_prazo · aparece 2x: "produto não funciona"
- **[13]** `a61e65fa` · nota 1 · automotivo · entrega no_prazo · aparece 1x: "Produto com defeito. Produto não funciona"
- **[15]** `51a15782` · nota 1 · informatica acessorios · entrega no_prazo · aparece 1x: "produto diferente do anunciado"
- **[16]** `ee36eb06` · nota 1 · pet shop · entrega no_prazo · aparece 1x: "Pedido entregue incompleto"
- **[17]** `0afdaef4` · nota 1 · beleza saude · entrega no_prazo · aparece 1x: "Recebi o produto incompleto, faltou 01 item!"
- **[18]** `e7bdc78c` · nota 1 · relogios presentes · entrega atrasada · aparece 1x: "Péssimo atendimento, não recomendo"
- **[19]** `d100adcd` · nota 2 · utilidades domesticas · entrega no_prazo · aparece 1x: "Pedido incompleto. Meu pedido chegou faltando um item"
- **[20]** `60d722b7` · nota 1 · brinquedos · entrega atrasada · aparece 1x: "Não recebi meu produto,e ja mandei mensagem pra loja mas ninguém me responde"
- **[21]** `8c6d55fb` · nota 1 · eletroportateis · entrega nao_entregue · aparece 1x: "Péssimo atendimento"
- **[22]** `47f083e5` · nota 1 · bebes · entrega atrasada · aparece 1x: "Produto não entregue e loja não deu satisfação após contato"
- **[24]** `a9761241` · nota 1 · moveis decoracao · entrega atrasada · aparece 1x: "Estou esperando meu estorno, a compra foi cancelada e não obtive nenhuma resposta é não recebi o estorno"
- **[25]** `b943aa9b` · nota 1 · consoles games · entrega nao_entregue · aparece 1x: "10 dias após efetuar a compra, gerar o boleto e pagar, recebo um e-mail cancelando a compra por falta do produto. Para o estorno do valor me obrigaram a ir em uma agência bancaria e retirar o valor!"
- **[26]** `7e46bb8d` · nota 1 · cama mesa banho · entrega atrasada · aparece 1x: "Compre ja tem dias e ate agora nao entregaram e nem me responde os meus contatos"
- **[28]** `e29c5edd` · nota 1 · beleza saude · entrega atrasada · aparece 1x: "Muito Absurdo !!! Insastisfeita com a compra devido a essa situação, ter que cancelar o oedido devido o mesmo não estar na unidade. A fatura do meu cartão tem vencimento dia 10. Espero que vocês res"
- **[29]** `c2f7b591` · nota 1 · consoles games · entrega nao_entregue · aparece 1x: "Insatisfação. Fiz uma compra q foi cancelada por vcs. Tentei por diversas vezes falar com vcs contudo não fui atendido. Não sei pq minha compra foi cancelada? Ninguém entrou em contato e não consigo ser atendido"
- **[30]** `b369ba48` · nota 1 · ferramentas jardim · entrega atrasada · aparece 1x: "Desrespeito com o cliente. Falta de respeito com o cliente"

## 5. Existem padrões recorrentes nas avaliações relacionadas à qualidade dos produtos?

- **Status:** `ok` | similaridade da pergunta: 0.8687 | intenção: neutra | subconsultas: 5

**Resposta:**

Sim, há padrões recorrentes, tanto negativos quanto positivos.

**1. Produto chegou quebrado**
Relatado em várias categorias: telefonia (repetido em 2 avaliações) [1], brinquedos [2][7], relógios/presentes [8] e eletrônicos [9]. Todas com entrega no prazo, o que sugere que o problema aparece mesmo sem atraso, mas as avaliações não indicam a causa.

**2. Produto com defeito ou que não funciona**
Aparece em automotivo [12][15], informática (repetido em 2 avaliações) [13], relógios/presentes [16] e telefonia [17]. Quase todas têm nota 1 ou 2.

**3. Baixa qualidade percebida**
Citada em informática [10], relógios/presentes [11], cama/mesa/banho [14][21] e esporte/lazer [19]. Notas entre 1 e 3.

**4. Elogios à qualidade e resistência**
Há relatos positivos de "ótima qualidade" em cama/mesa/banho (repetido em 16 e 3 avaliações) [3][4], "boa qualidade" em beleza/saúde (repetido em 12 avaliações) [22] e "material resistente" em automotivo, utilidades domésticas e malas [5][18][20].

**Ressalva:** os relatos negativos são variados e, individualmente, pouco repetidos. Já os positivos têm maior volume de repetição. Não é possível comparar proporções com segurança.

**Evidências citadas:**

- **[1]** `43bf7d48` · nota 1 · telefonia · entrega no_prazo · aparece 2x: "O produto chegou quebrado"
- **[2]** `03a673dc` · nota 2 · brinquedos · entrega no_prazo · aparece 1x: "Produto veio quebrado"
- **[3]** `34b941f9` · nota 5 · cama mesa banho · entrega no_prazo · aparece 16x: "Produto de ótima qualidade"
- **[4]** `7c80e9e0` · nota 4 · cama mesa banho · entrega no_prazo · aparece 3x: "Produto de ótima qualidade"
- **[5]** `0ac29099` · nota 5 · automotivo · entrega no_prazo · aparece 1x: "O produto excelente material resistente"
- **[7]** `1f9abf59` · nota 1 · brinquedos · entrega no_prazo · aparece 1x: "o produto veio quebrado"
- **[8]** `00eb718f` · nota 1 · relogios presentes · entrega no_prazo · aparece 1x: "Produto quebrado"
- **[9]** `29978e02` · nota 1 · eletronicos · entrega no_prazo · aparece 1x: "O produto estava quebrado"
- **[10]** `0d322bcc` · nota 2 · informatica acessorios · entrega no_prazo · aparece 1x: "Produto de baixa qualidade"
- **[11]** `846fd755` · nota 1 · relogios presentes · entrega no_prazo · aparece 1x: "Produto de baixa qualidade"
- **[12]** `002d6d96` · nota 2 · automotivo · entrega no_prazo · aparece 1x: "Produto não funciona"
- **[13]** `6d27bb9c` · nota 1 · informatica acessorios · entrega no_prazo · aparece 2x: "produto não funciona"
- **[14]** `630758cc` · nota 3 · cama mesa banho · entrega no_prazo · aparece 1x: "Produto com baixa qualidade"
- **[15]** `a61e65fa` · nota 1 · automotivo · entrega no_prazo · aparece 1x: "Produto com defeito. Produto não funciona"
- **[16]** `93f72220` · nota 1 · relogios presentes · entrega no_prazo · aparece 1x: "Produto já veio com defeito não funciona"
- **[17]** `2a58d04d` · nota 1 · telefonia · entrega no_prazo · aparece 1x: "produto não funciona bem"
- **[18]** `4ca66d8e` · nota 5 · utilidades domesticas · entrega no_prazo · aparece 1x: "Produto muito bom e com material resistente"
- **[19]** `be29016f` · nota 2 · esporte lazer · entrega no_prazo · aparece 1x: "Produtos de baixa qualidade"
- **[20]** `9700a96c` · nota 4 · malas acessorios · entrega no_prazo · aparece 1x: "produto muito bom, com material resistente"
- **[21]** `e9decc18` · nota 2 · cama mesa banho · entrega atrasada · aparece 1x: "Produto de muito baixa qualidade"
- **[22]** `29a2c76d` · nota 5 · beleza saude · entrega no_prazo · aparece 12x: "Produto de Boa Qualidade"

## 6. Quais avaliações sustentam a conclusão de que existem problemas recorrentes relacionados ao prazo de entrega?

- **Status:** `ok` | similaridade da pergunta: 0.9035 | intenção: problema | subconsultas: 4

**Resposta:**

**Sim, há evidência robusta de problemas recorrentes de prazo, em 4 temas:**

1. **Atraso explícito:** vários relatos de entrega atrasada, em categorias variadas. Exemplos: [7] (repetido em 6 avaliações), [12] (repetido em 5) e [16]. Também há menções a prazo vencido [18][25][26].

2. **Demora percebida, mesmo marcada "no prazo":** [20] (repetido em 7 avaliações), [11] e [13] (3 avaliações) reclamam de demora, apesar do status "no_prazo". Isso sugere divergência entre o prazo prometido e a expectativa do cliente, mas as avaliações não permitem confirmar a causa.

3. **Não entrega:** [2] (repetido em 13 avaliações), [1] (6 avaliações) e [5] relatam produto não entregue. Em [30], o cliente pede estorno após o prazo.

4. **Rastreio e Correios:** [22], [23] e [28] citam rastreio sem atualização, encomenda parada e atribuem o problema aos Correios. Esse é o relato do cliente, não uma causa comprovada.

**Ressalvas:** [4], [6] e [27] não sustentam a conclusão. [27] diz expressamente que a entrega foi no prazo.

**Evidências citadas:**

- **[1]** `0ccfc62c` · nota 1 · bebes · entrega atrasada · aparece 6x: "Produto não foi entregue"
- **[2]** `7ff39d79` · nota 1 · cool stuff · entrega atrasada · aparece 13x: "Produto não entregue"
- **[4]** `7e797e4f` · nota 1 · informatica acessorios · entrega no_prazo · aparece 1x: "Produto entregue errado"
- **[5]** `a1cdd61d` · nota 1 · telefonia · entrega atrasada · aparece 1x: "Produto nao foi entregue"
- **[6]** `361001c4` · nota 1 · esporte lazer · entrega no_prazo · aparece 1x: "produto entregue nao funciona"
- **[7]** `69528881` · nota 1 · papelaria · entrega atrasada · aparece 6x: "Atraso na entrega"
- **[11]** `214deaab` · nota 2 · informatica acessorios · entrega no_prazo · aparece 1x: "Demora demasiada na entrega"
- **[12]** `bb2810db` · nota 1 · automotivo · entrega atrasada · aparece 5x: "Muita demora na entrega"
- **[13]** `49cb1b45` · nota 2 · brinquedos · entrega no_prazo · aparece 3x: "Muita demora na entrega"
- **[16]** `9f5600c5` · nota 1 · moveis escritorio · entrega atrasada · aparece 1x: "entrega muito atrasada"
- **[18]** `2c74e9b8` · nota 1 · esporte lazer · entrega atrasada · aparece 1x: "Passou do prazo de entrega, demorou"
- **[20]** `97b1c66c` · nota 1 · cama mesa banho · entrega no_prazo · aparece 7x: "Demora na entrega"
- **[22]** `b7c1d885` · nota 1 · relogios presentes · entrega atrasada · aparece 1x: "Boa noite, não recebi o produto. Correios nunca atualizou o código de rastreio e nem uma posição da loja até o momento"
- **[23]** `d3ee1755` · nota 1 · papelaria · entrega atrasada · aparece 1x: "Os correios atrasaram a entrega e a encomenda esta parada la no centro de distribuicao"
- **[25]** `75d8bc14` · nota 1 · relogios presentes · entrega atrasada · aparece 1x: "Ñ compriu seu prazo de entrega"
- **[26]** `a5f1a48a` · nota 1 · utilidades domesticas · entrega atrasada · aparece 1x: "Quero saber o que aconteceu com a minha entrega, o prazo ja passou e nao tive satisfacao dos responsaveis"
- **[27]** `b1b8ed50` · nota 1 · ferramentas jardim · entrega no_prazo · aparece 1x: "Pedi duas cubas so recebi uma estou aguardando resposta de como posso resolver isso no mais a entrega foi no prazo e a que recebi e de boa qualidade"
- **[28]** `05481f96` · nota 1 · market place · entrega atrasada · aparece 1x: "nao recebi o produto acredito ser problema dos correios prazo de entrega expirou"
- **[30]** `f3bd714b` · nota 1 · automotivo · entrega atrasada · aparece 1x: "Produto nao foi entregue no prazo.. solicito o estorno do valor ja pago"

## 7. Qual é a capital da França?

- **Status:** `sem_evidencia` | similaridade da pergunta: 0.8117 | intenção: neutra | subconsultas: 0

**Resposta:**

Não encontrei avaliações na base que sustentem uma resposta para essa pergunta. A base contém avaliações de clientes de e-commerce (Olist, 2016-2018); tente perguntar sobre entrega, qualidade dos produtos, atendimento, elogios ou reclamações.

## 8. Quais são os principais problemas da economia brasileira?

- **Status:** `sem_evidencia` | similaridade da pergunta: 0.8494 | intenção: problema | subconsultas: 10

**Resposta:**

Não encontrei avaliações na base que sustentem uma resposta para essa pergunta. A base contém avaliações de clientes de e-commerce (Olist, 2016-2018); tente perguntar sobre entrega, qualidade dos produtos, atendimento, elogios ou reclamações.
