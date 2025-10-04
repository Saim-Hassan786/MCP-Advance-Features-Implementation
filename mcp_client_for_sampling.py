import asyncio
import json
from typing import Any
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from mcp.types import CreateMessageResult,CreateMessageRequestParams,ErrorData,TextContent
from mcp.shared.context import RequestContext
import google.generativeai as genai
genai.configure(api_key="AIzaSyBQFvTd1PBHg0i9s7UjNDCU9us_TK5IwMw")

async def llm_response(ctx:RequestContext["ClientSession",Any],params:CreateMessageRequestParams)->CreateMessageResult|ErrorData:
    print("Mock LLM Received Request From Server")
    print(f"Request Params: {params}")
    print(f"Context: {ctx}")
    print(f"Message: {params.messages}")
    print(f"Max Tokens: {params.maxTokens}")
    print(f"Temperature: {params.temperature}")
    print("LLM Generating Response...")

    try:
        messages = params.messages
        prompt = "\n".join(msg.content.text for msg in messages if isinstance(msg.content, TextContent))
        print(f"-> Client: Sending prompt to Gemini: {prompt}")
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(
            contents=prompt,
            generation_config=genai.GenerationConfig(
                max_output_tokens=params.maxTokens,
                temperature=params.temperature
            )
        )
        print("Response received from Gemini.")
        # print(response.text)
        return CreateMessageResult(
            role = "assistant",
            content = TextContent(type="text", text=response.text),
            model = model.model_name
        )
    except Exception as e:
        print(f"Error during LLM response generation: {e}")
        return ErrorData(
            message=str(e),
            code=32600,
            data={"details": str(e)}
        )
    
async def main():
    print("Starting MCP Client for Sampling...")
    server_url = "http://127.0.0.1:8000/mcp"
    async with streamablehttp_client(url=server_url) as (read_stream,write_stream,session_id):
        async with ClientSession(
            read_stream=read_stream,
            write_stream=write_stream,
            sampling_callback=llm_response
        ) as session:
            print("MCP Client connected to server.")
            await session.initialize()
            print("MCP Client session initialized.")
            
            topic = "a brave knight and a dragon"
            print(f"Requesting story generation about: {topic}")
            try:
                result = await session.call_tool(
                    name="sampling_tool",   
                    arguments={"topic": topic},
                )
                print("Story generation completed.")
                print("=================="*5)
                raw_text = result.content[0].text 
                parsed = json.loads(raw_text)
                story = parsed["content"]["text"]
                print(story)
            except Exception as e:
                print(f"Error during tool call: {e}")
        print("Demo Completed 🎈")

if __name__ == "__main__":
    asyncio.run(main())