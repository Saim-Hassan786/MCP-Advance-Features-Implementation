import asyncio
from pathlib import Path
from pydantic import FileUrl
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from mcp.shared.context import RequestContext
from mcp.types import ListRootsResult, Root

def _create_roots(path_list:list[str])->list[Root]:
    roots = []
    for path in path_list:
        p = Path(path).resolve()
        file_uri = FileUrl(f"file://{p}")
        roots.append(Root(
            uri=file_uri,
            name= p.name or "Root"
        ))
    return roots

async def handle_root_request_from_server(ctx:RequestContext["ClientSession",None])->ListRootsResult:
    root_paths = [str(Path.cwd().absolute())]
    return ListRootsResult(roots= _create_roots(root_paths))

async def main():
    server_url = "http://localhost:8000/mcp/"
    print(f"🚀 Connecting to MCP server at {server_url}")
    async with streamablehttp_client(url=server_url)as (read,write,session_id):
        async with ClientSession(
            read,
            write,
            list_roots_callback=handle_root_request_from_server
        ) as session:
            print("✅ Connected. Initializing session...")
            await session.initialize()
            print("🛠️ Session initialized with roots capability.")
            print("\n-> Client: Calling analyze_project tool...")
            result = await session.call_tool(
                name= "Root Tool"
            )
            print("\n🔍 Project Analysis Results:", result)
    print("\n✅ Demo complete!")

if __name__ == "__main__":
    asyncio.run(main())