# System Patterns

## Architecture

- `src` layout with package structure
- Thin service layer (`JiraClient`) wrapping `atlassian-python-api`
- MCP layer (`JiraMcpServer`) exposing tools via FastMCP
- Console entry `mcp-jira` runs stdio or SSE server

## Component Structure

```
src/
├── __init__.py          # Package marker
├── config.py            # Configuration management
├── jira_client.py       # Jira API client wrapper
├── server.py            # MCP server and tools
├── cli.py               # CLI entry point
└── app.py               # Inspector support
```

## Key Patterns

### Configuration
- Environment-based via `JiraConfig` dataclass
- Required: `JIRA_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN`
- Optional: `JIRA_DEFAULT_PROJECT` for convenience
- Loaded at startup from environment

### Client Layer
- `JiraClient` wraps `atlassian-python-api`
- Provides clean interface for issue operations
- Handles authentication automatically
- Returns raw API responses (JSON)

### MCP Server Layer
- `JiraMcpServer` registers tools via `@_server.tool()` decorator
- `_safe()` wrapper for consistent error handling
- Returns structured responses: `{"success": bool, "data"/"error": Any}`
- Tool implementations call client methods

### Transport
- **stdio**: Default for direct CLI usage and development
- **sse**: HTTP/SSE transport for Docker deployment
- CLI supports `--transport`, `--port`, `--host` arguments
- Environment variables: `MCP_TRANSPORT`, `MCP_PORT`, `MCP_HOST`

### Error Handling
- All tool calls wrapped in `_safe()` method
- Exceptions caught and returned as `{"success": false, "error": "..."}`
- Structured logging via `structlog`

### Assignee Field Handling
- Auto-detects Jira Cloud vs Server format
- If assignee contains ":" → uses `{"accountId": value}` (Jira Cloud)
- Otherwise → uses `{"name": value}` (Jira Server)
- Example accountId: `"712020:af6d11d4-1824-4a43-97e4-964ba3318f82"`
- Use `searchUsers` tool to find accountId from email/username

## Operational Patterns

### Development
- Use stdio transport for testing
- MCP Inspector: `uv run --with mcp mcp dev src/app.py --with-editable .`
- Absolute path to `uv` in Cursor config for reliability

### Production (Docker)
- HTTP/SSE transport for network communication
- Single container serves multiple client connections
- Health checks via `/sse` endpoint
- Resource limits: 512M memory limit, 128M reservation

### Multi-Project Support
- Separate docker-compose files per project
- Different ports (9001, 9002, etc.)
- Project-specific `.env.project1`, `.env.project2` files
- Each container runs independently

## Integration with FastMCP

- FastMCP handles MCP protocol details
- Tools defined with type hints and Pydantic Field descriptions
- Automatic parameter validation
- Built-in stdio and SSE transport support

