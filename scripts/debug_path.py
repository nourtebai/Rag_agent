import asyncio
import sys
sys.path.insert(0, ".")

from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from app.agent.graph import build_graph


async def trace(question: str):
    graph = build_graph()
    result = await graph.ainvoke({
        "messages": [HumanMessage(content=question)],
        "route": "",
        "rag_found": True,
    })

    print(f"Route du Supervisor : {result['route']}")
    print(f"RAG a trouvé une réponse : {result['rag_found']}")

    tool_calls_seen = [
        m.name for m in result["messages"] if isinstance(m, ToolMessage)
    ]
    print(f"Outils appelés dans l'ordre : {tool_calls_seen}")

    if result["route"] == "direct":
        chemin = "DIRECT (pas d'outil)"
    elif result["rag_found"]:
        chemin = "SEARCH → RAG (trouvé)"
    else:
        chemin = "SEARCH → RAG (échec) → WEB"

    print(f"Chemin emprunté : {chemin}")
    print("\nRéponse finale :", result["messages"][-1].content)


asyncio.run(trace(sys.argv[1]))