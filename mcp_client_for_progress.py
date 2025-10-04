import asyncio
from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession

async def progress_handler(progress: float, total: float | None, message: str | None):
    if total:
        percentage = (progress / total) * 100
        progress_bar = "█" * int(percentage // 5) + "░" * (20 - int(percentage // 5))
        print(f"    📊 [{progress_bar}] {percentage:.1f}% - {message or 'Working...'}")
    else:
        print(f"    📊 Progress: {progress} - {message or 'Working...'}")

async def main():
    server_url = "http://127.0.0.1:8000/mcp"
    async with streamablehttp_client(url= server_url) as (read,write,session_id):
        async with ClientSession(
            read_stream= read,
            write_stream= write,
        ) as session:
            print("✅ Connected to MCP server!")
            init_result = await session.initialize()
            print(f"🔧 Server capabilities: {init_result.capabilities}")
            tools_result = await session.list_tools()
            print(f"🛠️ Available tools: {[tool.name for tool in tools_result.tools]}")
            result_1 = await session.call_tool(
                name="MCP Progress Bar TOOL",
                arguments={
                    "file_size": 10,
                    "file_name" :"Interstellar_Movie"
                },
                progress_callback=progress_handler
            )
            print(result_1.content[0].text)
            print("=" * 40)
            result_2 = await session.call_tool(
                name = "Process Data",
                arguments={
                    "records" : 100
                },
                progress_callback= progress_handler
            )
            print(result_2.content[0].text)
            
    print("🎉 Demo completed!")
    print("\n💡 Progress updates were sent in real-time via MCP protocol!")

if __name__ == "__main__":
    asyncio.run(main()) 
        