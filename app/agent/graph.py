from typing import Literal, TypedDict

from langchain_core.messages import AnyMessage, HumanMessage, AIMessage
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain_mcp_adapters.client import MultiServerMCPClient

from app.config import settings

NOT_FOUND_PHRASE = "je ne trouve pas cette information dans les documents fournis"

SUPERVISOR_PROMPT = """Classe cette question dans une seule catégorie : search, ou direct.
'search' = la question demande une information factuelle, peu importe si elle se trouve dans des documents internes ou sur le web.
'direct' = question conversationnelle simple (salutations, remerciements, questions sur toi en tant qu'assistant).

Réponds UNIQUEMENT par un mot : search, ou direct. Aucune ponctuation, aucune explication."""

RAG_PROMPT = f"""Tu réponds en utilisant l'outil search_knowledge_base.
Cite tes sources (fichier, page).
Si l'outil ne renvoie rien de pertinent pour répondre à la question, réponds EXACTEMENT et UNIQUEMENT par :
"Je ne trouve pas cette information dans les documents fournis."
sans rien ajouter d'autre."""

WEB_PROMPT = """Tu réponds en utilisant l'outil web_search.
Cite tes sources (URL). Si l'outil ne trouve rien de pertinent, dis-le clairement."""


class AgentState(TypedDict):
    messages: list[AnyMessage]
    route: str
    rag_found: bool


def get_llm(temperature: float = 0):
    return ChatOllama(model=settings.llm_model, base_url=settings.ollama_base_url, temperature=temperature)


async def get_mcp_tools():
    client = MultiServerMCPClient({
        "rag": {
            "command": "python",
            "args": ["app/mcp_tools/server.py"],
            "transport": "stdio",
        }
    })
    return await client.get_tools()


def supervisor_node(state: AgentState) -> dict:
    llm = get_llm()
    question = state["messages"][-1].content
    raw = llm.invoke([("system", SUPERVISOR_PROMPT), ("human", question)]).content.strip().lower()
    route = "search" if "search" in raw else "direct"
    return {"route": route}


async def rag_node(state: AgentState) -> dict:
    tools = await get_mcp_tools()
    rag_tool = [t for t in tools if t.name == "search_knowledge_base"]
    llm = get_llm().bind_tools(rag_tool, tool_choice="search_knowledge_base")
    messages = [("system", RAG_PROMPT)] + state["messages"]
    response = llm.invoke(messages)

    tool_node = ToolNode(rag_tool)
    tool_results = await tool_node.ainvoke({"messages": [response]})
    final = llm.invoke(messages + [response] + tool_results["messages"])

    found = NOT_FOUND_PHRASE not in final.content.strip().lower()
    return {
        "messages": state["messages"] + [response] + tool_results["messages"] + [final],
        "rag_found": found,
    }


async def web_node(state: AgentState) -> dict:
    tools = await get_mcp_tools()
    web_tool = [t for t in tools if t.name == "web_search"]
    llm = get_llm().bind_tools(web_tool, tool_choice="web_search")
    messages = [("system", WEB_PROMPT), ("human", state["messages"][0].content)]
    response = llm.invoke(messages)

    tool_node = ToolNode(web_tool)
    tool_results = await tool_node.ainvoke({"messages": [response]})
    final = llm.invoke(messages + [response] + tool_results["messages"])

    return {"messages": state["messages"] + [response] + tool_results["messages"] + [final]}


def direct_node(state: AgentState) -> dict:
    llm = get_llm()
    response = llm.invoke(state["messages"])
    return {"messages": state["messages"] + [response]}


def route_from_supervisor(state: AgentState) -> Literal["rag", "direct"]:
    return "rag" if state["route"] == "search" else "direct"


def route_from_rag(state: AgentState) -> Literal["end", "web"]:
    return "end" if state["rag_found"] else "web"


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("supervisor", supervisor_node)
    graph.add_node("rag", rag_node)
    graph.add_node("web", web_node)
    graph.add_node("direct", direct_node)

    graph.add_edge(START, "supervisor")
    graph.add_conditional_edges("supervisor", route_from_supervisor, {"rag": "rag", "direct": "direct"})
    graph.add_conditional_edges("rag", route_from_rag, {"end": END, "web": "web"})
    graph.add_edge("web", END)
    graph.add_edge("direct", END)

    return graph.compile()


async def run_agent(question: str) -> str:
    app = build_graph()
    result = await app.ainvoke({"messages": [HumanMessage(content=question)], "route": "", "rag_found": True})
    return result["messages"][-1].content