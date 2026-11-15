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
