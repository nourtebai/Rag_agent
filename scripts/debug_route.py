import asyncio
import sys
sys.path.insert(0, ".")

from app.agent.graph import supervisor_node
from langchain_core.messages import HumanMessage

question = sys.argv[1]
result = supervisor_node({"messages": [HumanMessage(content=question)], "route": ""})
print("Route choisie :", result["route"])