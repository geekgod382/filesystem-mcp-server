"""
Filesystem MCP Server - Pure MCP SDK Implementation
Provides tools and resources for file system operations
"""
import asyncio
import json
import logging
import os
import shutil
from pathlib import Path
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (Tool, TextContent, CallToolResult, ListToolsResult, GetPromptResult, ListPromptsResult, PromptMessage, ListResourcesResult, ReadResourceResult, Resource, Prompt)

# Configure logging to stderr (important for stdio transport)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]  # This writes to stderr by default
)
logger = logging.getLogger(__name__)

# Create the MCP server
server = Server("filesystem-server")

# Configuration: Set allowed directories (security measure)
ALLOWED_PATHS = [str(Path.home())]

def is_path_allowed(path: str) -> bool:
    """Check if a path is within allowed directories"""
    abs_path = os.path.abspath(path)
    return any(abs_path.startswith(allowed) for allowed in ALLOWED_PATHS)

# TOOLS HANDLERS
@server.list_tools()
async def list_tools() -> ListToolsResult:
    """List available tools"""
    tools = [
        Tool(
            name="read_file_tool",
            description="Read the contents of a file",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string", 
                        "description": "Absolute or relative path to the file"
                    },
                    "encoding": {
                        "type": "string",
                        "description": "File encoding (default: utf-8)",
                        "default": "utf-8"
                    }
                },
                "required": ["path"]
            }
        ),
        Tool(
            name="write_file_tool",
            description="Write content to a file (creates or overwrites)",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Absolute or relative path to the file"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write"
                    },
                    "encoding": {
                        "type": "string",
                        "description": "File encoding (default: utf-8)",
                        "default": "utf-8"
                    }
                },
                "required": ["path", "content"]
            }
        ),
        Tool(
            name="list_directory_tool",
            description="List contents of a directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Absolute or relative path to the directory"
                    },
                    "recursive": {
                        "type": "boolean",
                        "description": "If True, list subdirectories recursively",
                        "default": False
                    }
                },
                "required": ["path"]
            }
        ),
        Tool(
            name="create_directory_tool",
            description="Create a new directory (creates parent directories if needed)",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Absolute or relative path to the directory"
                    }
                },
                "required": ["path"]
            }
        ),
        Tool(
            name="delete_file_tool",
            description="Delete a file",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Absolute or relative path to the file"
                    }
                },
                "required": ["path"]
            }
        ),
        Tool(
            name="delete_directory_tool",
            description="Delete a directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Absolute or relative path to the directory"
                    },
                    "recursive": {
                        "type": "boolean",
                        "description": "If True, delete directory and all contents",
                        "default": False
                    }
                },
                "required": ["path"]
            }
        ),
        Tool(
            name="move_file_tool",
            description="Move or rename a file or directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "source": {
                        "type": "string",
                        "description": "Source path"
                    },
                    "destination": {
                        "type": "string",
                        "description": "Destination path"
                    }
                },
                "required": ["source", "destination"]
            }
        ),
        Tool(
            name="copy_file_tool",
            description="Copy a file or directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "source": {
                        "type": "string",
                        "description": "Source path"
                    },
                    "destination": {
                        "type": "string",
                        "description": "Destination path"
                    }
                },
                "required": ["source", "destination"]
            }
        ),
        Tool(
            name="search_files_tool",
            description="Search for files matching a pattern",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "Directory to search in"
                    },
                    "pattern": {
                        "type": "string",
                        "description": "Filename pattern (supports wildcards like *.txt)"
                    },
                    "recursive": {
                        "type": "boolean",
                        "description": "If True, search subdirectories",
                        "default": True
                    }
                },
                "required": ["directory", "pattern"]
            }
        ),
        Tool(
            name="get_file_info_tool",
            description="Get detailed information about a file or directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Absolute or relative path"
                    }
                },
                "required": ["path"]
            }
        )
    ]
    
    return ListToolsResult(tools=tools)

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> CallToolResult:
    """Handle tool calls"""
    try:
        if name == "read_file_tool":
            return await read_file_tool(arguments)
        elif name == "write_file_tool":
            return await write_file_tool(arguments)
        elif name == "list_directory_tool":
            return await list_directory_tool(arguments)
        elif name == "create_directory_tool":
            return await create_directory_tool(arguments)
        elif name == "delete_file_tool":
            return await delete_file_tool(arguments)
        elif name == "delete_directory_tool":
            return await delete_directory_tool(arguments)
        elif name == "move_file_tool":
            return await move_file_tool(arguments)
        elif name == "copy_file_tool":
            return await copy_file_tool(arguments)
        elif name == "search_files_tool":
            return await search_files_tool(arguments)
        elif name == "get_file_info_tool":
            return await get_file_info_tool(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
    except Exception as e:
        logger.error(f"Error in {name}: {str(e)}")
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: {str(e)}")]
        )

# Tool implementations
async def read_file_tool(arguments: dict) -> CallToolResult:
    """Read the contents of a file"""
    path = arguments["path"]
    encoding = arguments.get("encoding", "utf-8")
    
    if not is_path_allowed(path):
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: Access denied to {path}")]
        )
    
    if not os.path.exists(path):
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: File not found: {path}")]
        )
    
    if not os.path.isfile(path):
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: Not a file: {path}")]
        )
    
    try:
        with open(path, 'r', encoding=encoding) as f:
            content = f.read()
        
        result = {
            "path": path,
            "content": content,
            "size": len(content),
            "encoding": encoding
        }
        
        return CallToolResult(
            content=[TextContent(type="text", text=json.dumps(result, indent=2))]
        )
    except UnicodeDecodeError:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: Cannot decode file with {encoding} encoding")]
        )
    except Exception as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error reading file: {str(e)}")]
        )

async def write_file_tool(arguments: dict) -> CallToolResult:
    """Write content to a file"""
    path = arguments["path"]
    content = arguments["content"]
    encoding = arguments.get("encoding", "utf-8")
    
    if not is_path_allowed(path):
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: Access denied to {path}")]
        )
    
    try:
        # Create parent directories if they don't exist
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        
        with open(path, 'w', encoding=encoding) as f:
            f.write(content)
        
        result = {
            "success": True,
            "path": path,
            "bytes_written": len(content.encode(encoding))
        }
        
        return CallToolResult(
            content=[TextContent(type="text", text=json.dumps(result, indent=2))]
        )
    except Exception as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error writing file: {str(e)}")]
        )

async def list_directory_tool(arguments: dict) -> CallToolResult:
    """List contents of a directory"""
    path = arguments["path"]
    recursive = arguments.get("recursive", False)
    
    if not is_path_allowed(path):
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: Access denied to {path}")]
        )
    
    if not os.path.exists(path):
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: Directory not found: {path}")]
        )
    
    if not os.path.isdir(path):
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: Not a directory: {path}")]
        )
    
    try:
        entries = []
        
        if recursive:
            for root, dirs, files in os.walk(path):
                for name in dirs + files:
                    item_path = os.path.join(root, name)
                    stat = os.stat(item_path)
                    entries.append({
                        "path": item_path,
                        "name": name,
                        "type": "directory" if os.path.isdir(item_path) else "file",
                        "size": stat.st_size,
                        "modified": stat.st_mtime
                    })
        else:
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                stat = os.stat(item_path)
                entries.append({
                    "path": item_path,
                    "name": item,
                    "type": "directory" if os.path.isdir(item_path) else "file",
                    "size": stat.st_size,
                    "modified": stat.st_mtime
                })
        
        result = {
            "path": path,
            "count": len(entries),
            "entries": entries
        }
        
        return CallToolResult(
            content=[TextContent(type="text", text=json.dumps(result, indent=2))]
        )
    except Exception as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error listing directory: {str(e)}")]
        )

async def create_directory_tool(arguments: dict) -> CallToolResult:
    """Create a new directory"""
    path = arguments["path"]
    
    if not is_path_allowed(path):
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: Access denied to {path}")]
        )
    
    try:
        os.makedirs(path, exist_ok=True)
        result = {
            "success": True,
            "path": path,
            "message": "Directory created successfully"
        }
        return CallToolResult(
            content=[TextContent(type="text", text=json.dumps(result, indent=2))]
        )
    except Exception as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error creating directory: {str(e)}")]
        )

async def delete_file_tool(arguments: dict) -> CallToolResult:
    """Delete a file"""
    path = arguments["path"]
    
    if not is_path_allowed(path):
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: Access denied to {path}")]
        )
    
    if not os.path.exists(path):
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: File not found: {path}")]
        )
    
    if not os.path.isfile(path):
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: Not a file: {path}")]
        )
    
    try:
        os.remove(path)
        result = {
            "success": True,
            "path": path,
            "message": "File deleted successfully"
        }
        return CallToolResult(
            content=[TextContent(type="text", text=json.dumps(result, indent=2))]
        )
    except Exception as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error deleting file: {str(e)}")]
        )

async def delete_directory_tool(arguments: dict) -> CallToolResult:
    """Delete a directory"""
    path = arguments["path"]
    recursive = arguments.get("recursive", False)
    
    if not is_path_allowed(path):
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: Access denied to {path}")]
        )
    
    if not os.path.exists(path):
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: Directory not found: {path}")]
        )
    
    if not os.path.isdir(path):
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: Not a directory: {path}")]
        )
    
    try:
        if recursive:
            shutil.rmtree(path)
        else:
            os.rmdir(path)
        
        result = {
            "success": True,
            "path": path,
            "message": "Directory deleted successfully"
        }
        return CallToolResult(
            content=[TextContent(type="text", text=json.dumps(result, indent=2))]
        )
    except Exception as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error deleting directory: {str(e)}")]
        )

async def move_file_tool(arguments: dict) -> CallToolResult:
    """Move or rename a file or directory"""
    source = arguments["source"]
    destination = arguments["destination"]
    
    if not is_path_allowed(source) or not is_path_allowed(destination):
        return CallToolResult(
            content=[TextContent(type="text", text="Error: Access denied")]
        )
    
    if not os.path.exists(source):
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: Source not found: {source}")]
        )
    
    try:
        shutil.move(source, destination)
        result = {
            "success": True,
            "source": source,
            "destination": destination,
            "message": "Moved successfully"
        }
        return CallToolResult(
            content=[TextContent(type="text", text=json.dumps(result, indent=2))]
        )
    except Exception as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error moving: {str(e)}")]
        )

async def copy_file_tool(arguments: dict) -> CallToolResult:
    """Copy a file or directory"""
    source = arguments["source"]
    destination = arguments["destination"]
    
    if not is_path_allowed(source) or not is_path_allowed(destination):
        return CallToolResult(
            content=[TextContent(type="text", text="Error: Access denied")]
        )
    
    if not os.path.exists(source):
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: Source not found: {source}")]
        )
    
    try:
        if os.path.isfile(source):
            shutil.copy2(source, destination)
        else:
            shutil.copytree(source, destination)
        
        result = {
            "success": True,
            "source": source,
            "destination": destination,
            "message": "Copied successfully"
        }
        return CallToolResult(
            content=[TextContent(type="text", text=json.dumps(result, indent=2))]
        )
    except Exception as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error copying: {str(e)}")]
        )

async def search_files_tool(arguments: dict) -> CallToolResult:
    """Search for files matching a pattern"""
    directory = arguments["directory"]
    pattern = arguments["pattern"]
    recursive = arguments.get("recursive", True)
    
    if not is_path_allowed(directory):
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: Access denied to {directory}")]
        )
    
    if not os.path.exists(directory):
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: Directory not found: {directory}")]
        )
    
    try:
        path_obj = Path(directory)
        if recursive:
            matches = list(path_obj.rglob(pattern))
        else:
            matches = list(path_obj.glob(pattern))
        
        results = [str(match) for match in matches]
        
        result = {
            "directory": directory,
            "pattern": pattern,
            "count": len(results),
            "matches": results
        }
        
        return CallToolResult(
            content=[TextContent(type="text", text=json.dumps(result, indent=2))]
        )
    except Exception as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error searching: {str(e)}")]
        )

async def get_file_info_tool(arguments: dict) -> CallToolResult:
    """Get detailed information about a file or directory"""
    path = arguments["path"]
    
    if not is_path_allowed(path):
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: Access denied to {path}")]
        )
    
    if not os.path.exists(path):
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: Path not found: {path}")]
        )
    
    try:
        stat = os.stat(path)
        abs_path = os.path.abspath(path)
        
        info = {
            "path": abs_path,
            "name": os.path.basename(path),
            "type": "directory" if os.path.isdir(path) else "file",
            "size": stat.st_size,
            "created": stat.st_ctime,
            "modified": stat.st_mtime,
            "accessed": stat.st_atime,
            "permissions": oct(stat.st_mode)[-3:],
        }
        
        if os.path.isfile(path):
            info["extension"] = os.path.splitext(path)[1]
        
        return CallToolResult(
            content=[TextContent(type="text", text=json.dumps(info, indent=2))]
        )
    except Exception as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error getting file info: {str(e)}")]
        )

# RESOURCES HANDLERS
@server.list_resources()
async def list_resources() -> ListResourcesResult:
    """List available resources"""
    resources = [
        Resource(
            uri="file://*",
            name="File Contents",
            description="Read the contents of any file by providing its path",
            mimeType="text/plain"
        ),
        Resource(
            uri="directory://*",
            name="Directory Listing",
            description="List the contents of any directory by providing its path",
            mimeType="application/json"
        )
    ]
    
    return ListResourcesResult(resources=resources)

@server.read_resource()
async def read_resource(uri: str) -> ReadResourceResult:
    """Read a resource"""
    if uri.startswith("file://"):
        path = uri[7:]  # Remove "file://" prefix
        
        if not is_path_allowed(path):
            return ReadResourceResult(
                contents=[TextContent(type="text", text=f"Error: Access denied to {path}")]
            )
        
        if not os.path.exists(path) or not os.path.isfile(path):
            return ReadResourceResult(
                contents=[TextContent(type="text", text=f"Error: File not found or not a file: {path}")]
            )
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            return ReadResourceResult(
                contents=[TextContent(type="text", text=content)]
            )
        except Exception as e:
            return ReadResourceResult(
                contents=[TextContent(type="text", text=f"Error reading file: {str(e)}")]
            )
    
    elif uri.startswith("directory://"):
        path = uri[12:]  # Remove "directory://" prefix
        
        if not is_path_allowed(path):
            return ReadResourceResult(
                contents=[TextContent(type="text", text=f"Error: Access denied to {path}")]
            )
        
        if not os.path.exists(path) or not os.path.isdir(path):
            return ReadResourceResult(
                contents=[TextContent(type="text", text=f"Error: Directory not found or not a directory: {path}")]
            )
        
        try:
            entries = []
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                stat = os.stat(item_path)
                entries.append({
                    "name": item,
                    "type": "directory" if os.path.isdir(item_path) else "file",
                    "size": stat.st_size,
                    "modified": stat.st_mtime
                })
            
            return ReadResourceResult(
                contents=[TextContent(type="text", text=json.dumps(entries, indent=2))]
            )
        except Exception as e:
            return ReadResourceResult(
                contents=[TextContent(type="text", text=f"Error listing directory: {str(e)}")]
            )
    
    else:
        return ReadResourceResult(
            contents=[TextContent(type="text", text="Error: Unsupported resource URI")]
        )

# PROMPTS HANDLERS
@server.list_prompts()
async def list_prompts() -> ListPromptsResult:
    """List available prompts"""
    prompts = [
        Prompt(
            name="analyze_directory",
            description="Generate a prompt to analyze a directory structure",
            arguments=[
                {
                    "name": "directory",
                    "description": "Directory path to analyze",
                    "required": True
                }
            ]
        ),
        Prompt(
            name="find_and_read",
            description="Generate a prompt to find and read files matching a pattern",
            arguments=[
                {
                    "name": "directory",
                    "description": "Directory to search in", 
                    "required": True
                },
                {
                    "name": "pattern",
                    "description": "File pattern to search for",
                    "required": True
                }
            ]
        )
    ]
    
    return ListPromptsResult(prompts=prompts)

@server.get_prompt()
async def get_prompt(name: str, arguments: dict) -> GetPromptResult:
    """Get a prompt"""
    if name == "analyze_directory":
        directory = arguments["directory"]
        content = f"""Please analyze the directory structure at: {directory}

Use the list_directory_tool to explore the directory and provide insights about:
1. Total number of files and directories
2. File types and their distribution
3. Largest files
4. Directory organization
5. Any potential issues or recommendations"""
        
        return GetPromptResult(
            description=f"Analysis prompt for directory: {directory}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=content)
                )
            ]
        )
    
    elif name == "find_and_read":
        directory = arguments["directory"]
        pattern = arguments["pattern"]
        content = f"""Please find and read files in: {directory}
Pattern: {pattern}

1. Use search_files_tool to find matching files
2. Use read_file_tool to read the contents
3. Provide a summary of what you found"""
        
        return GetPromptResult(
            description=f"Find and read prompt for {pattern} in {directory}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=content)
                )
            ]
        )
    
    else:
        raise ValueError(f"Unknown prompt: {name}")

async def main():
    """Main entry point for the server"""
    # Use stdio transport
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())