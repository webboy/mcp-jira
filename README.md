## mcp-jira
Python MCP server for Jira Cloud (REST API v3), built with FastMCP and atlassian-python-api. It exposes tools for issue management (CRUD, search, transitions, comments, attachments) so AI clients (e.g., Cursor) can safely automate Jira workflows.

### Requirements
- Python 3.10+
- uv (`pipx install uv` or follow uv docs)
- Jira Cloud account with API token
  - Create API token at: https://id.atlassian.com/manage-profile/security/api-tokens

### Install (editable)
```bash
uv pip install -e .
```

### Docker Usage (HTTP/SSE Transport)

The MCP server runs in a Docker container using HTTP/SSE transport, allowing a single long-running container that handles multiple Cursor connections.

#### Quick Start

1. **Create environment file:**
```bash
cp .env.example .env
# Edit .env with your Jira credentials
```

2. **Build and start the container:**
```bash
docker-compose up -d --build
```

3. **Configure Cursor** (`~/.cursor/mcp.json`):
```json
{
  "mcpServers": {
    "jira": {
      "url": "http://localhost:9001/sse"
    }
  }
}
```

4. **Restart Cursor** - The Jira MCP server should now be available!

#### Manual Docker Commands

**Build the image:**
```bash
docker build -t mcp-jira:latest .
```

**Run with docker-compose:**
```bash
# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

**Run with docker directly:**
```bash
docker run -d \
  --name mcp-jira \
  -p 9001:9001 \
  -e JIRA_URL=https://your-domain.atlassian.net \
  -e JIRA_EMAIL=your.email@example.com \
  -e JIRA_API_TOKEN=your_api_token \
  -e JIRA_DEFAULT_PROJECT=PROJ \
  -e MCP_TRANSPORT=sse \
  mcp-jira:latest
```

#### Health Check

Verify the server is running:
```bash
curl http://localhost:9001/sse
```

#### Container Management

```bash
# Check if running
docker ps | grep mcp-jira

# View logs
docker logs mcp-jira

# Restart
docker restart mcp-jira

# Stop and remove
docker stop mcp-jira
docker rm mcp-jira
```

#### Benefits of HTTP/SSE Transport

- **Single container**: One long-running container handles all requests
- **Multiple connections**: Cursor can connect/reconnect without spawning new containers
- **Better performance**: No container startup overhead per request
- **Easier debugging**: View logs with `docker logs`
- **Health monitoring**: Built-in health checks

#### Multi-Project Setup

If you work on multiple Jira instances with different credentials, you can run multiple containers:

**Setup:**
1. Create project-specific env files:
```bash
cp .env.project1.example .env.project1
cp .env.project2.example .env.project2
# Edit each with the appropriate credentials
```

2. Start both containers:
```bash
docker compose -f docker-compose.project1.yml up -d
docker compose -f docker-compose.project2.yml up -d
```

3. Configure Cursor with both servers:
```json
{
  "mcpServers": {
    "jira-project1": {
      "url": "http://localhost:9001/sse"
    },
    "jira-project2": {
      "url": "http://localhost:9002/sse"
    }
  }
}
```

**Management:**
```bash
# Start all projects
docker compose -f docker-compose.project1.yml up -d
docker compose -f docker-compose.project2.yml up -d

# Stop specific project
docker compose -f docker-compose.project1.yml down

# View logs for specific project
docker compose -f docker-compose.project1.yml logs -f
```

### Configuration
Environment variables:
- JIRA_URL: Your Jira Cloud instance URL (e.g., `https://your-company.atlassian.net`)
- JIRA_EMAIL: Your Jira account email
- JIRA_API_TOKEN: API token from https://id.atlassian.com/manage-profile/security/api-tokens
- JIRA_DEFAULT_PROJECT: Default project key (optional but convenient)
- FASTMCP_LOG_LEVEL: DEBUG|INFO|... (optional)

### Run (stdio server)
```bash
JIRA_URL='https://your-domain.atlassian.net' \
JIRA_EMAIL='your.email@example.com' \
JIRA_API_TOKEN='your_api_token' \
JIRA_DEFAULT_PROJECT='PROJ' \
uv run mcp-jira
```
The server uses stdio and prints little until a client connects.

### Debug with MCP Inspector
Expose a FastMCP instance via `src/app.py` and launch the Inspector:
```bash
JIRA_URL='https://your-domain.atlassian.net' \
JIRA_EMAIL='your.email@example.com' \
JIRA_API_TOKEN='your_api_token' \
JIRA_DEFAULT_PROJECT='PROJ' \
uv run --with mcp mcp dev src/app.py --with-editable .
```
Open the printed URL and call tools like `health` and `getProjects`.

### Use with Cursor (Native/Development)

#### Option 1: Docker (Recommended for Production)
See [Docker Usage](#docker-usage-httpsse-transport) section above.

#### Option 2: Direct UV (for Development)
If Cursor runs inside the same Ubuntu WSL2 environment, prefer an absolute path to `uv` and add editable source to ensure the local tree is used:
```json
{
  "mcpServers": {
    "jira": {
      "command": "/home/nemanja/.local/bin/uv",
      "args": ["run", "--with-editable", "/home/nemanja/projects/mcp/mcp-jira", "mcp-jira"],
      "env": {
        "JIRA_URL": "https://your-domain.atlassian.net",
        "JIRA_EMAIL": "your.email@example.com",
        "JIRA_API_TOKEN": "your_api_token",
        "JIRA_DEFAULT_PROJECT": "PROJ",
        "FASTMCP_LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

#### Option 3: WSL Bridge (Windows)
If Cursor runs on Windows (outside WSL), bridge to WSL via:
```json
{
  "mcpServers": {
    "jira": {
      "command": "wsl",
      "args": [
        "bash", "-lc",
        "cd /home/<user>/projects/mcp/mcp-jira && JIRA_URL='https://your-domain.atlassian.net' JIRA_EMAIL='your.email@example.com' JIRA_API_TOKEN='your_api_token' JIRA_DEFAULT_PROJECT='PROJ' /home/<user>/.local/bin/uv run mcp-jira"
      ]
    }
  }
}
```

### Tools (high-level)

**Health & Configuration:**
- `health` - Validate configuration and Jira connectivity

**Issue Operations:**
- `getIssue` - Get detailed information about an issue
- `createIssue` - Create a new issue with summary, description, type, priority, assignee, labels
- `updateIssue` - Update issue fields (summary, description, priority, assignee, labels)
- `searchIssues` - Search issues using JQL (Jira Query Language)

**Transitions & Workflow:**
- `getTransitions` - Get available status transitions for an issue
- `transitionIssue` - Move issue to a different status (e.g., To Do → In Progress)

**Comments:**
- `addComment` - Add a comment to an issue
- `getComments` - Get all comments for an issue

**Attachments:**
- `addAttachment` - Add a file attachment to an issue (base64-encoded)

**Project & Metadata:**
- `getProjects` - List all accessible projects
- `getProject` - Get detailed information about a specific project
- `getIssueTypes` - Get available issue types for a project

All tools return MCP-compatible responses (JSON with success/error status).

### Common Use Cases

**Create an issue:**
```
Use the createIssue tool:
- project: "PROJ"
- summary: "Implement new feature"
- description: "Detailed description here"
- issue_type: "Task"
```

**Search for issues:**
```
Use the searchIssues tool with JQL:
- jql: "project = PROJ AND status = 'In Progress'"
- max_results: 10
```

**Transition an issue:**
```
1. First, use getTransitions to see available transitions
2. Then use transitionIssue with the transition ID
```

**Add a comment:**
```
Use the addComment tool:
- issue_key: "PROJ-123"
- comment: "Work in progress, will update soon"
```

### Troubleshooting

**No tools in client:**
- Ensure the command actually starts in your environment (absolute path to `uv` helps)
- Add `FASTMCP_LOG_LEVEL=DEBUG` to see detailed logs
- Check that all required environment variables are set

**401/403 errors:**
- Verify API token is correct and not expired
- Check that your Jira account has proper permissions
- Ensure JIRA_URL is correct (include https://, no trailing slash)

**Connection errors:**
- Verify JIRA_URL is accessible from your network
- Check if you need to be on VPN for corporate Jira instances
- Test connectivity: `curl https://your-domain.atlassian.net`

**Docker container not starting:**
- Check logs: `docker logs mcp-jira`
- Verify .env file exists and has correct values
- Ensure port 9001 is not already in use

**Inspector won't connect:**
- Ensure proxy health at `http://localhost:6277/health` returns `{ "status": "ok" }`
- If bridging from Windows to WSL, enable localhost forwarding in WSL

### Security

- Treat API tokens as secrets. Never commit them to version control.
- Use `.env` files (which are gitignored) for local development
- For production, use Docker secrets or environment variable injection
- Rotate API tokens if exposed
- API tokens at: https://id.atlassian.com/manage-profile/security/api-tokens

### License

MIT License - see LICENSE file for details

