# Tech Context

## Technology Stack

- **Python**: >= 3.10 (for modern type hints and dataclasses)
- **UV**: Dependency and project management (PEP 621 `pyproject.toml`)
- **Build backend**: Hatchling
- **MCP SDK**: `mcp[cli]>=1.2.0` (Python MCP SDK with CLI tools)
- **Jira SDK**: `atlassian-python-api>=3.41.0` (comprehensive Jira Cloud support)
- **HTTP Client**: `httpx>=0.27` (used by atlassian-python-api)
- **Validation**: `pydantic>=2.7` (MCP parameter validation)
- **Logging**: `structlog>=24.1.0` (structured logging)
- **ASGI Server**: `uvicorn>=0.30.0` (for SSE transport)
- **Web Framework**: `starlette>=0.37.0` (SSE transport routing)

## Project Structure

```
mcp-jira/
├── src/                    # Source code
│   ├── __init__.py
│   ├── config.py           # Configuration management
│   ├── jira_client.py      # Jira API client
│   ├── server.py           # MCP server
│   ├── cli.py              # CLI entry point
│   └── app.py              # Inspector support
├── memory-bank/            # Project documentation
├── pyproject.toml          # Project configuration
├── Dockerfile              # Docker image
├── docker-compose.yml      # Docker orchestration
├── .env.example            # Environment template
├── .gitignore              # Git ignore rules
└── README.md               # User documentation
```

## Docker Support

### Base Image
- `python:3.10-slim` for minimal footprint
- UV installed in container for dependency management
- Non-root user (`mcp`, UID 1000) for security

### Networking
- **HTTP/SSE transport** for network-based communication
- Single long-running container serves multiple connections
- Port **9001** exposed (vs Bitbucket's 9000)
- Health checks for monitoring

### Configuration
- `.env` file for docker-compose
- Environment variables for credentials and settings
- Image size optimized via `.dockerignore`

### Transport Modes

**stdio** (Default for CLI):
- Standard input/output communication
- Used for direct CLI usage and development
- Command: `mcp-jira` or `uv run mcp-jira`

**sse** (Default for Docker):
- HTTP Server-Sent Events transport
- Network-based, allows multiple clients
- Routes: `/sse` (GET - SSE connection), `/messages` (POST - client messages)
- Command: `mcp-jira --transport sse --port 9001`

## Configuration Approach

### Development (Direct UV)
```json
{
  "command": "uv",
  "args": ["run", "--with-editable", "/path/to/mcp-jira", "mcp-jira"],
  "env": {
    "JIRA_URL": "https://...",
    "JIRA_EMAIL": "...",
    "JIRA_API_TOKEN": "..."
  }
}
```

### Production (Docker)
1. Create `.env` file with credentials
2. Start container: `docker compose up -d`
3. Configure Cursor: `{"url": "http://localhost:9001/sse"}`
4. Cursor connects to running container via HTTP/SSE

## Deployment

### Single Instance
```bash
docker compose up -d
```

### Multi-Project
```bash
docker compose -f docker-compose.project1.yml up -d  # Port 9001
docker compose -f docker-compose.project2.yml up -d  # Port 9002
```

## Technical Implementation Details

### FastMCP Integration
- `FastMCP` class from `mcp.server.fastmcp`
- Tools registered via `@_server.tool()` decorator
- Automatic parameter validation with Pydantic
- Type hints + `Annotated[Type, Field(description="...")]` for documentation

### SSE Transport
- `SseServerTransport` from `mcp.server.sse`
- Starlette ASGI app for routing
- Uvicorn as ASGI server
- Routes handled asynchronously

### Authentication
- Jira Cloud: Email + API Token
- API token created at: https://id.atlassian.com/manage-profile/security/api-tokens
- Passed to `atlassian-python-api` constructor
- Stored in environment variables (never in code)

## Development Tools

### MCP Inspector
```bash
uv run --with mcp mcp dev src/app.py --with-editable .
```
Opens web interface for testing tools interactively

### Logging
- `structlog` for structured logging
- Configurable via `FASTMCP_LOG_LEVEL` (DEBUG, INFO, WARNING, ERROR)
- Logs include context (tool name, parameters, errors)

### Testing Connectivity
```bash
# Health check
curl http://localhost:9001/sse

# Container logs
docker logs mcp-jira

# Direct test
JIRA_URL=... JIRA_EMAIL=... JIRA_API_TOKEN=... uv run mcp-jira
```

