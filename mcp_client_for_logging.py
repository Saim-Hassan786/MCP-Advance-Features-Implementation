import asyncio
from mcp import ClientSession
from mcp.types import LoggingMessageNotificationParams
from mcp.client.streamable_http import streamablehttp_client

async def logging_handler(params:LoggingMessageNotificationParams):
    emoji_map = {
        "debug": "🔍",
        "info": "📰",
        "warning": "⚠️",
        "error": "❌",
    }
    emoji = emoji_map.get(params.level.lower(), "📝")
    logger_info = f" [{params.logger}]" if params.logger else ""
    print(f"    {emoji} [{params.level.upper()}]{logger_info} {params.data}")

async def main():
    server_url = "http://127.0.0.1:8000/mcp"
    async with streamablehttp_client(server_url) as (read_stream,write_stream,session_id):
        async with ClientSession(
            read_stream=read_stream,
            write_stream=write_stream,
            logging_callback=logging_handler
        ) as client:
            print("Initializing Session")
            await client.initialize()
            print("Session SuccessFully Initialized")
            print("Calling The Tool")
            print("\nSCENARIO 1: Successful processing")
            print("-" * 40)
            result = await client.call_tool(
                name= "MCP LOGGER TOOL",
                arguments = {
                    "item_id":123,
                    "should_fail" : False
                }
            )
            print(result.content[0].text)
            print("=" * 40)

            print("\nSCENARIO 2: Processing with failure")
            print("-" * 40)
            result = await client.call_tool(
                name= "MCP LOGGER TOOL",
                arguments = {
                    "item_id":123,
                    "should_fail" : True
                }
            )
            print(result.content[0].text)
    print("\n🎉 Demo finished.")

if __name__ == "__main__":
    asyncio.run(main())