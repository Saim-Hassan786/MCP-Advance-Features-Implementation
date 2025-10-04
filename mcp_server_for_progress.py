import asyncio
import logging
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.server import Context

# Setup logging for our console
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP(
    name = "MCP SERVER FOR PROGRESS LOGS",
    stateless_http= False
)

@mcp.tool(
    name = "MCP Progress Bar TOOL",
    description= "Mcp progress logs",
    title= "MCP PROGRESS"
)
async def file_download(ctx:Context,file_size:int,file_name:str):
    await ctx.info(f"Starting the download file {file_name} of size {file_size}")
    total_chunks = file_size * 10  
    for chunk in range(total_chunks + 1):
        progress = chunk
        percentage = (chunk / total_chunks) * 100
        await ctx.report_progress(
            progress = progress,
            total= total_chunks,
            message=f"Downloading {file_name}... {percentage:.1f}%"
        )
        await asyncio.sleep(0.5)
    await ctx.info(f"Successfully Downloaded File {file_name}")
    return f"{file_name} downloaded Successfully"

@mcp.tool(
    name = "Process Data",
    description= " Processes The Userdata and Show Progress Logs",
    title = "Data Processor"
)
async def data_processor(records:int,ctx:Context):
    await ctx.info(f"Starting to process {records} records")
    
    for i in range(records + 1):
        if i == 0:
            message = "Initializing data processor..."
        elif i < records // 4:
            message = "Loading and validating records..."
        elif i < records // 2:
            message = "Applying transformations..."
        elif i < records * 3 // 4:
            message = "Running calculations..."
        else:
            message = "Finalizing results..."
        await asyncio.sleep(0.05)
        await ctx.report_progress(
            progress= i,
            total= records,
            message=message
        )
        await asyncio.sleep(0.05)
    
    await ctx.info("Operation Successful")
    return f"Records Progress Successfully Demonstrated of Records {records}"

mcp_app = mcp.streamable_http_app()