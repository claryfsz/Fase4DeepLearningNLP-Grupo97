"""Funções de embedding compartilhadas entre a base (MC) e o pipeline (L).

Importante: o modelo e5 foi treinado com prefixos diferentes para
documentos e perguntas. Por isso a L deve SEMPRE usar `embed_query`
para a pergunta do usuário, e nunca o modelo direto.
"""
from functools import lru_cache

from sentence_transformers import SentenceTransformer

from src.config import EMBEDDING_BATCH_SIZE, EMBEDDING_MODEL


@lru_cache(maxsize=1)
def get_model() -> SentenceTransformer:
    return SentenceTransformer(EMBEDDING_MODEL)


def embed_passages(textos: list[str], show_progress: bool = True) -> list[list[float]]:
    """Gera embeddings dos documentos (avaliações) para indexação."""
    vetores = get_model().encode(
        [f"passage: {t}" for t in textos],
        batch_size=EMBEDDING_BATCH_SIZE,
        normalize_embeddings=True,  # vetores unitários -> distância cosseno estável
        show_progress_bar=show_progress,
    )
    return vetores.tolist()


def embed_query(pergunta: str) -> list[float]:
    """Gera o embedding da pergunta do usuário (uso da L no pipeline RAG)."""
    vetor = get_model().encode(f"query: {pergunta}", normalize_embeddings=True)
    return vetor.tolist()
