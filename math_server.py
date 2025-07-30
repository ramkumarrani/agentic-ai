from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Math")

@mcp.tool()
def add (a: int, b: int) -> int:
    "simple add operation"
    return a+b

@mcp.tool()
def multiply(a: int, b:int) -> int:
    "simple multiple operation"
    return a*b

@mcp.tool()
def subtract(a: int, b:int) -> int:
    "simple subtract operation"
    return a-b

@mcp.tool()
def divide(a: int, b:int) -> int:
    "simple division operation"
    return a/b
    
if __name__ == "__main__":
    mcp.run(transport="stdio")    
