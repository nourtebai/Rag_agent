from sentence_transformers import CrossEncoder

_reranker = None


def get_reranker() -> CrossEncoder:
    global _reranker
    if _reranker is None:
        _reranker = CrossEncoder("cross-encoder/mmarco-mMiniLMv2-L12-H384-v1")
    return _reranker


def rerank(query: str, chunks: list[dict], top_n: int = 4) -> list[dict]:
    if not chunks:
        return []

    pairs = [(query, c["content"]) for c in chunks]
    scores = get_reranker().predict(pairs)

    for chunk, score in zip(chunks, scores):
        chunk["score"] = float(score)

    return sorted(chunks, key=lambda c: c["score"], reverse=True)[:top_n]