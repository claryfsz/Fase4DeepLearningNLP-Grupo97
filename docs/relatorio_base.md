# Relatório da base de conhecimento

Gerado automaticamente por `python -m src.data_prep`.

## Funil de preparação

| Etapa | Avaliações | % do total |
|---|---:|---:|
| Base original | 99,224 | 100% |
| Após remover `review_id` duplicado | 98,410 | 99.2% |
| Com título ou comentário | 42,291 | 42.6% |
| Com pelo menos 3 caracteres | 42,026 | 42.4% |
| Após agrupar textos idênticos (documentos indexados) | 36,510 | 36.8% |

## Valores ausentes na base original

- Sem título: 87,656 (88.3%)
- Sem comentário: 58,247 (58.7%)

## Distribuição de notas

| Nota | Base original | Documentos indexados |
|---|---:|---:|
| 1 | 11,424 | 8,344 |
| 2 | 3,151 | 2,095 |
| 3 | 8,179 | 3,356 |
| 4 | 19,142 | 5,277 |
| 5 | 57,328 | 17,438 |

## Tamanho dos documentos (caracteres)

Média 77.8, mediana 62.0, mínimo 3, máximo 229.

## Situação da entrega (documentos indexados)

- no_prazo: 30,827
- atrasada: 3,936
- nao_entregue: 1,747

## 10 categorias com mais documentos

- cama mesa banho: 3,704
- beleza saude: 2,997
- esporte lazer: 2,586
- informatica acessorios: 2,399
- relogios presentes: 2,279
- moveis decoracao: 2,263
- utilidades domesticas: 2,096
- telefonia: 1,650
- automotivo: 1,496
- ferramentas jardim: 1,374
