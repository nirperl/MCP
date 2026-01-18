# agent_loop.py
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Define how to start your server
server_params = StdioServerParameters(command="python", args=["server.py"])


async def healing_loop():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Step 1: Run Tests
            print("🔍 Running tests...")
            test_output = await session.call_tool("run_tests", {})

            if "FAILED" in test_output:
                print("❌ Tests failed. Analyzing...")
                # Step 2: Ask the LLM to analyze and fix
                # (You would pass 'test_output' to your LLM here)
                # For now, let's think: what information does the LLM need most?