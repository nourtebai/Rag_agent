import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from mcp.server.fastmcp import FastMCP

from app.retrieval.retriever import search

mcp = FastMCP("rag-knowledge-base")


@mcp.tool()
def search_knowledge_base(query: str) -> str:
    """Recherche des informations dans les documents indexés (notes réglementaires,
    procédures internes, etc.). Utilise cet outil pour toute question factuelle
    sur le contenu des documents. N'invente jamais une réponse sans l'avoir utilisé."""
    results = search(query, k=4)

    if not results:
        return "Aucun résultat trouvé dans les documents."

    blocks = []
    for r in results:
        pages = r["pages"][0] if r["pages"] else "?"
        blocks.append(f"(source: {r['source']}, page {pages})\n{r['content']}")

    return "\n\n---\n\n".join(blocks)


if __name__ == "__main__":
    mcp.run(transport="stdio")