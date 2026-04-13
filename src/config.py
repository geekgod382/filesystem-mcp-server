from pathlib import Path
import os
import logging
from mcp.server import Server

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Create the MCP server
server = Server("filesystem-server")


ALLOWED_PATHS = [str(Path.home())]

def is_path_allowed(path):
    abs_path = os.path.realpath(path)  # resolves symlinks too
    for allowed in ALLOWED_PATHS:
        allowed_normalized = os.path.realpath(allowed)
        # Ensure that the allowed path ends with separator before prefix check
        if not allowed_normalized.endswith(os.sep):
            allowed_normalized += os.sep
        # check exact match
        if abs_path == os.path.realpath(allowed) or abs_path.startswith(allowed_normalized):
            return True
    return False
