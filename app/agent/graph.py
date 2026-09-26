from typing import Literal, TypedDict

from langchain_core.messages import AnyMessage, HumanMessage
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain_mcp_adapters.client import MultiServerMCPClient

from app.config import settings

ROUTER_PROMPT = """Tu classifies une question utilisateur en une seule catégorie :
- "rag" : la question porte sur le contenu de documents (notes réglementaires, procédures, chiffres, faits spécifiques).
- "direct" : la question est générale, conversationnelle, ou ne nécessite pas de recherche documentaire.

Réponds uniquement par "rag" ou "direct", rien d'autre."""

RAG_PROMPT = """Tu réponds en utilisant l'outil search_knowledge_base.
Cite tes sources (fichier, page). Si l'outil ne trouve rien, dis-le clairement."""


class AgentState(TypedDict):
    messages: list[AnyMessage]
    route: str


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
    decision = llm.invoke([("system", ROUTER_PROMPT), ("human", question)]).content.strip().lower()
    route = "rag" if "rag" in decision else "direct"
    return {"route": route}


async def rag_node(state: AgentState) -> dict:
    tools = await get_mcp_tools()
    llm = get_llm().bind_tools(tools)
    messages = [("system", RAG_PROMPT)] + state["messages"]
    response = llm.invoke(messages)

    if response.tool_calls:
        tool_node = ToolNode(tools)
        tool_results = await tool_node.ainvoke({"messages": [response]})
        final = llm.invoke(messages + [response] + tool_results["messages"])
        return {"messages": state["messages"] + [response] + tool_results["messages"] + [final]}

    return {"messages": state["messages"] + [response]}


def direct_node(state: AgentState) -> dict:
    llm = get_llm()
    response = llm.invoke(state["messages"])
    return {"messages": state["messages"] + [response]}


def route_decision(state: AgentState) -> Literal["rag", "direct"]:
    return state["route"]


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("supervisor", supervisor_node)
    graph.add_node("rag", rag_node)
    graph.add_node("direct", direct_node)

    graph.add_edge(START, "supervisor")
    graph.add_conditional_edges("supervisor", route_decision, {"rag": "rag", "direct": "direct"})
    graph.add_edge("rag", END)
    graph.add_edge("direct", END)

    return graph.compile()


async def run_agent(question: str) -> str:
    app = build_graph()
    result = await app.ainvoke({"messages": [HumanMessage(content=question)], "route": ""})
    return result["messages"][-1].content