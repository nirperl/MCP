import asyncio
import os
from google import genai
from google.genai import types
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# 1. Configuration
model_key = os.getenv("GEMINI_API_KEY") #os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=model_key)
model_id = "gemini-2.0-flash"  # High-speed model great for automation loops

# Path to your server.py file
server_params = StdioServerParameters(command="python", args=["server.py"])


async def healing_loop():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # --- 2. Initial Test Run ---
            print("🔍 Running tests via MCP...")
            test_output = await asyncio.wait_for(session.call_tool("run_tests", {}), timeout=60)
            test_results = test_output.content[0].text if test_output.content else ""

            if "FAILED" in test_results:
                print("❌ Tests failed. Starting Gemini healing loop...")

                # Read the code directly to simplify the agent's job
                with open("logic.py", "r") as f:
                    code_content = f.read()

                # --- 3. Discover MCP Tools ---
                mcp_tools = await session.list_tools()
                gemini_tools = types.Tool(
                    function_declarations=[
                        types.FunctionDeclaration(
                            name=tool.name,
                            description=tool.description,
                            parameters=tool.inputSchema,
                        ) for tool in mcp_tools.tools
                    ]
                )

                # --- 4. Agentic Reasoning & Fixing ---
                prompt = (
                    f"The unit tests failed.\n\n"
                    f"Test Output:\n{test_results}\n\n"
                    f"Current logic.py:\n{code_content}\n\n"
                    f"Please apply a fix to logic.py."
                )

                response = client.models.generate_content(
                    model=model_id,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        tools=[gemini_tools],
                        temperature=0
                    )
                )

                # --- 5. Handle Tool Calls ---
                if response.candidates[0].content.parts[0].function_call:
                    fc = response.candidates[0].content.parts[0].function_call
                    print(f"🛠️ Gemini decided to call: {fc.name}")

                    result = await session.call_tool(fc.name, fc.args)
                    print(f"✅ Fix applied! Result: {result.content[0].text}")


if __name__ == "__main__":
    asyncio.run(healing_loop())