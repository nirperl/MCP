# server.py
from mcp.server.fastmcp import FastMCP
import subprocess

mcp = FastMCP("SelfHealer")

@mcp.tool()
def read_source_code(file_path: str) -> str:
    """Reads the content of a source file."""
    with open(file_path, "r") as f:
        return f.read()

@mcp.tool()
def run_tests() -> str:
    """Runs pytest and returns the output."""
    result = subprocess.run(["pytest", "tests.py"], capture_output=True, text=True)
    return result.stdout + result.stderr

@mcp.tool()
def apply_fix(file_path: str, new_content: str):
    """Overwrites a file with a proposed fix."""
    with open(file_path, "w") as f:
        f.write(new_content)


if __name__ == '__main__':
    mcp.run()