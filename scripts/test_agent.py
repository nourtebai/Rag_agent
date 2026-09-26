import asyncio
import sys
sys.path.insert(0, ".")

from app.agent.graph import run_agent

print(asyncio.run(run_agent(sys.argv[1])))