from __future__ import annotations

from config import load_config_from_env
from server import JiraMcpServer


# Expose a FastMCP instance for the MCP CLI / Inspector
_jira_server = JiraMcpServer(config=load_config_from_env())

# The MCP CLI searches for one of these variable names
app = _jira_server._server  # FastMCP instance
server = app
mcp = app

