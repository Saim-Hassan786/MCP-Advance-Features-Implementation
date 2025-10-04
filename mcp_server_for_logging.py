import asyncio
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.server import Context
from mcp.types import TextContent
from mcp import types

mcp = FastMCP(
    name="MCP LOG Server",
    stateless_http=False
)

@mcp.tool(
    name="MCP LOGGER TOOL",
    description="Logs Info About the server working",
    title="MCP LOGGER EVENT"
)
async def logger_func(ctx:Context,item_id:int,should_fail:bool)-> list[types.TextContent]:
    await ctx.info(f"Starting the Function Call On the Server")
    await asyncio.sleep(0.5)
    await ctx.debug(f"Sending Logs for the item against item_id {item_id}")
    await asyncio.sleep(0.5)
    await ctx.debug(f"The condition received with the request is {should_fail}")
    await asyncio.sleep(0.5)

    if should_fail:
        await ctx.warning(f"System Cannot Proceed further against the Id {item_id}")
        await asyncio.sleep(0.5)
        await ctx.error(f"Cannot Proceed Any Further against the Item {item_id} CRITICAL FAILURE ")
        await asyncio.sleep(0.5)
        return [TextContent(
            type="text",
            text=f"Failed to process the item against the item_id {item_id}"
        )]
    
    await ctx.info(f"Successfully Implemented The Logic")
    await asyncio.sleep(0.5)
    return [TextContent(
        type= "text",
        text= f"Successful Operation Against the Id {item_id}"
    )]

mcp_app = mcp.streamable_http_app()