from mcp.server.fastmcp import FastMCP,Context
from mcp.types import SamplingMessage,TextContent

mcp = FastMCP(
    name="Sampling Server",
    stateless_http=False
)

@mcp.tool(
    name="sampling_tool",
    description="A tool for sampling messages",
    title="Sampling Tool",
)
async def story_generator(ctx:Context,topic:str):
    print("Sending sampling message...")
    print(f"Generating story about: {topic}")
    prompt = f"Generate a short story about {topic}."
    try:
        result = await ctx.session.create_message(
            messages=[
                SamplingMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=prompt
                    )
                )
            ],
            max_tokens=5000,
            temperature=0.7
        )
        print("Received response from sampling message.")
        print(f"Story: {result}")
        return result
    except Exception as e:
        print(f"Error during sampling message: {e}")
        return f"Error generating story due to: {e}"

mcp_app = mcp.streamable_http_app()


