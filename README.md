# Filesystem MCP Server

A Model Context Protocol (MCP) server that provides comprehensive file system access and operations. This server allows AI assistants to interact with your file system through a standardized interface.

## Features

### Resources (Read-only access)
- **file://{path}** - Read file contents
- **directory://{path}** - List directory contents with metadata

### Tools (File Operations)
- **read_file_tool** - Read file contents with encoding support
- **write_file_tool** - Create or overwrite files
- **list_directory_tool** - List directory contents (recursive option)
- **create_directory_tool** - Create directories with parent creation
- **delete_file_tool** - Delete files
- **delete_directory_tool** - Delete directories (recursive option)
- **move_file_tool** - Move or rename files/directories
- **copy_file_tool** - Copy files or directories
- **search_files_tool** - Search for files by pattern (supports wildcards)
- **get_file_info_tool** - Get detailed file/directory metadata

### Prompts
- **analyze_directory_prompt** - Template for directory analysis
- **find_and_read_prompt** - Template for finding and reading files

## Security

By default, the server restricts access to your home directory. You can modify the `ALLOWED_PATHS` list in `server.py` to change this.

```python
ALLOWED_PATHS = [str(Path.home())]  # Modify this to add more paths
```

- Access is limited to a configured root directory
- No access to system paths
- User must explicitly grant permissions


## Server Versions

**server.py** - Pure MCP SDK implementation (currently active)
- Uses `mcp.server.Server` directly
- Better compatibility with Claude Desktop
- Lower-level control

### Using with Claude Desktop

To use this server with Claude Desktop, add it to your Claude configuration file.

1. Open your Claude Desktop config file:
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

2. Add the server configuration:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "python",
      "args": ["C:\\Users\\<username>\\filesystem-mcp-server\\server.py"]
    }
  }
}
```

3. Restart Claude Desktop

### Using with MCP Inspector

You can test and debug your server with the MCP Inspector:

```powershell
npx @modelcontextprotocol/inspector python server.py
```

## Example Usage

Once connected to an MCP client (like Claude Desktop), you can:

### List files in a directory
```
Can you list the files in my Documents folder?
```

### Read a file
```
Read the contents of C:\Users\<username>\test.txt
```

### Search for files
```
Find all Python files in my projects directory
```

### Create and write to a file
```
Create a new file called notes.txt with the content "Hello World"
```

### Get file information
```
Get detailed information about myfile.pdf
```

## Project Structure

```
filesystem-mcp-server/
├── server.py           # Main MCP server implementation
├── requirements.txt    # Python dependencies
├── test_server        # Test file
└── README.md          # This file
```

## Extending the Server

You can easily add more tools by following the existing patterns:

```python
@mcp.tool()
def your_custom_tool(param: str) -> dict:
    """Description of your tool"""
    # Your implementation
    return {"result": "success"}
```

## Troubleshooting

### Permission Errors
If you get permission errors, check that the path is within `ALLOWED_PATHS` in `server.py`.

### Server Not Responding
Check that the server is running with stdio transport and that your client is properly configured.

## Requirements

- Python 3.8 or higher
- Windows (adaptable to Linux/macOS by changing path separators)
- MCP Python SDK 1.25 or higher

## Resources

- [MCP Documentation](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [FastMCP Documentation](https://modelcontextprotocol.github.io/python-sdk/)