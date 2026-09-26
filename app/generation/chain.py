from langchain_ollama import ChatOllama

from app.config import settings
from app.retrieval.retriever import search

SYSTEM_PROMPT = """Tu es un assistant qui répond UNIQUEMENT à partir du contexte fourni.

Règles strictes :
- Si la réponse n'est pas dans le contexte, dis clairement : "Je ne trouve pas cette information dans les documents fournis."
- Ne complète jamais avec tes connaissances générales.
- Cite tes sources après chaque affirmation, sous la forme (source, page X).
- Sois concis et précis.
"""


def _format_context(chunks: list[dict]) -> str:
    blocks = []
    for i, c in enumerate(chunks, 1):
        pages = c["pages"][0] if c["pages"] else "?"
        blocks.append(f"[Extrait {i}] (source: {c['source']}, page {pages})\n{c['content']}")
    return "\n\n".join(blocks)


def answer(query: str, k: int = 4) -> dict:
    chunks = search(query, k=k)

    if not chunks:
        return {"answer": "Aucun document pertinent trouvé.", "sources": []}

    context = _format_context(chunks)
    llm = ChatOllama(model=settings.llm_model, base_url=settings.ollama_base_url, temperature=0)

    messages = [
        ("system", SYSTEM_PROMPT),
        ("human", f"Contexte :\n{context}\n\nQuestion : {query}"),
    ]

    response = llm.invoke(messages)

    return {
        "answer": response.content,
        "sources": [
            {"source": c["source"], "pages": c["pages"], "score": c["score"]}
            for c in chunks
        ],
    }