from app.retrieval.hybrid import hybrid_search
from app.retrieval.reranker import rerank


def search(query: str, k: int = 4) -> list[dict]:
    """Pipeline complet : recherche hybride (large) → reranking (précis) → top k."""
    candidates = hybrid_search(query, k=20)
    return rerank(query, candidates, top_n=k)