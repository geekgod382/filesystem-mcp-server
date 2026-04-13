from src.config import server
from mcp.server.stdio import stdio_server
from src import tools, resources, prompts, tool_schemas
import asyncio

server.list_tools()(tool_schemas.list_tools)
server.call_tool()(tools.call_tool)
server.list_resources()(resources.list_resources)
server.read_resource()(resources.read_resource)
server.list_prompts()(prompts.list_prompts)
server.get_prompt()(prompts.get_prompt)

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())

