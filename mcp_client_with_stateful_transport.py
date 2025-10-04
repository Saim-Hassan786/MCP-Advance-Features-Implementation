import asyncio
import httpx
import json

async def initialize_mcp(client,url):
    print("Step 1: Initialize The MCP client...")
    print("Initializing MCP client...")
    json_payload = {
        "jsonrpc": "2.0",
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-06-18",
            "capabilities":{
                "roots":{
                    "listChanged":True
                },
                "elicitations":{},
                "sampling":{}
            },
            "clientInfo":{
                    "name":"Test Client For Server",
                    "title":"Test Client",
                    "version":"1.0.0"
                }
            }
        ,
        "id": 1
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json,text/event-stream"
    }
    print(f"Sending initialization request to {url}...")
    response = await client.post(url, json=json_payload,headers=headers)
    print("Initialization response received.")
    print("Response Status Code:", response.status_code)
    print("Response Content:", response.text)
    session_id = response.headers.get("mcp-session-id")
    if session_id:
        print(f"Session ID received: {session_id}")
    else:
        print("No Session ID received.")
    return session_id

async def initialize_notification(client,url,session_id):
    print("Step 2: Initialize The Notification...")
    print("Initializing Notification...")
    json_payload = {
        "jsonrpc": "2.0",
        "method": "notifications/initialized",
    }

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json,text/event-stream",
        "MCP-Protocol-Version": "2025-06-18",
        "mcp-session-id": session_id
    }
    print(f"Sending notification initialization request to {url}...")
    response = await client.post(url, json=json_payload,headers=headers)
    print("Notification initialization Sent.")

async def list_tools_request(client,url,session_id):
    print("Step 3: List The Tools...")
    print("Listing Tools...")
    json_payload = {
        "jsonrpc": "2.0",
        "method": "tools/list",
        "params": {},
        "id": 2
    }

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json,text/event-stream",
        "MCP-Protocol-Version": "2025-06-18",
        "mcp-session-id": session_id
    }
    print(f"Sending list tools request to {url}...")
    response = await client.post(url, json=json_payload,headers=headers)
    print("List tools response received.")
    print("Response Status Code:", response.status_code)
    print("Response Content:", response)
    async for line in response.aiter_lines():
        if line.startswith("data:"):
                    data_json = line[len("data: "):]  
                    data = json.loads(data_json)     
                    tools = data.get("result", {}).get("tools", [])
                    print("Tools listed successfully:")
                    for tool in tools:
                        print(f"- {tool['name']}: {tool.get('title', 'No title')}")

async def tool_call_request(client,url,session_id):
    print("Step 4: Call The Tool...")
    print("Calling Tool...")
    json_payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "Weather Tool",
            "arguments": {
                "location": "Lahore"
            }
        },
        "id": 3
    }

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json,text/event-stream",
        "MCP-Protocol-Version": "2025-06-18",
        "mcp-session-id": session_id
    }
    print(f"Sending tool call request to {url}...")
    async with client.stream("POST", url, json=json_payload,headers=headers) as response:
        print("Tool call response received.")
        print("Response Status Code:", response.status_code)
        async for line in response.aiter_lines():
            if line:
                print("Received line:", line)
    print(f"Tool call request completed: {response}")
    print(f"Tool call complete Result: {response}")

async def main():
    url = "http://127.0.0.1:8000/mcp"
    async with httpx.AsyncClient() as client:
        print("Request Initialization")
        session_id = await initialize_mcp(client,url)
        if session_id:
            print(f"Session ID obtained, proceeding with further requests.{session_id}")
            print("Request Notification Initialization")
            await initialize_notification(client,url,session_id)
            print("Request List Tools")
            await list_tools_request(client,url,session_id)
            print("Request Tool Call")
            await tool_call_request(client,url,session_id)
        else:
            print("Failed to obtain session ID. Exiting.")

if __name__ == "__main__":
    asyncio.run(main())
        


