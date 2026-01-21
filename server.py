# server.py
import asyncio
import sys
import subprocess
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("SelfHealer")

@mcp.tool()
def read_source_code(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def execute():
    return subprocess.run(
        [sys.executable, "-m", "pytest", "tests.py", "--no-header"],
        capture_output=True,
        text=True,
        encoding="utf-8"
    )

@mcp.tool()
async def run_tests() -> str:
    print("Server: Starting pytest...", file=sys.stderr)
    try:
        result = await asyncio.to_thread(execute)
        return result.stdout + result.stderr
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return str(e)

@mcp.tool()
def apply_fix(file_path: str, new_content: str):
    """Overwrites a file with a proposed fix."""
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)


if __name__ == '__main__':
    mcp.run()