from app.retrieval.store import get_vector_store


def search(query: str, k: int = 4) -> list[dict]:
    """Return the k most relevant chunks for a query, with scores and sources."""
    store = get_vector_store()
    results = store.similarity_search_with_score(query, k=k)

    return [
        {
            "content": doc.page_content,
            "source": doc.metadata.get("source"),
            "pages": doc.metadata.get("pages"),
            "headings": doc.metadata.get("headings"),
            "score": score,
        }
        for doc, score in results
    ]