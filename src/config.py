"""Configurações centrais do projeto (caminhos, modelo e coleção vetorial).

MC e L importam daqui para garantir que a base e o pipeline usem
exatamente o mesmo modelo de embeddings e a mesma coleção.
"""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Dados
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
REVIEWS_CSV = RAW_DIR / "olist_order_reviews_dataset.csv"
ORDERS_CSV = RAW_DIR / "olist_orders_dataset.csv"
ORDER_ITEMS_CSV = RAW_DIR / "olist_order_items_dataset.csv"
PRODUCTS_CSV = RAW_DIR / "olist_products_dataset.csv"
KAGGLE_URL = "https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce"
ARQUIVOS_NECESSARIOS = [REVIEWS_CSV, ORDERS_CSV, ORDER_ITEMS_CSV, PRODUCTS_CSV]
DOCUMENTS_PARQUET = PROCESSED_DIR / "documentos.parquet"
EDA_REPORT = ROOT / "docs" / "relatorio_base.md"

# Banco vetorial
# No Windows, o ChromaDB falha ao abrir o índice HNSW em caminhos com acento
# (ex.: "Área de Trabalho") ou dentro do OneDrive. Nesses casos, defina
# VOC_CHROMA_DIR com um caminho simples, ex.: C:\chroma_voc
CHROMA_DIR = Path(os.getenv("VOC_CHROMA_DIR", ROOT / "data" / "chroma"))
COLLECTION_NAME = "avaliacoes_olist"

# Embeddings
# multilingual-e5-small: multilíngue (as avaliações são em português),
# leve o bastante para rodar em CPU e treinado para busca semântica.
# Exige os prefixos "query: " (perguntas) e "passage: " (documentos).
EMBEDDING_MODEL = "intfloat/multilingual-e5-small"
EMBEDDING_BATCH_SIZE = 64

# Limpeza
MIN_CHARS = 3  # textos menores que isso ("ok", "." etc.) não carregam informação
