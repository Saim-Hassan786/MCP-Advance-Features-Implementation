from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    name="Stateful MCP Server",
    stateless_http=False
)

@mcp.tool(
    name="Weather Tool",
    description="Provides weather information for a given location.",
    title="Get Weather"
)
async def weather_tool(location: str) -> str:
    return f"The weather in {location} is sunny with a high of 75°F."

@mcp.tool(
    name="Multiplication Tool",
    description="Performs basic arithmetic operations.",
    title="Multiply"
)
async def multiply_tool(a:int,b:int) -> str:
    try:
        result = a * b
        return f"The result of {a} multiplied by {b} is {result}."   
    except Exception as e:
        return f"Error in calculation: {str(e)}"
    
mcp_app = mcp.streamable_http_app()