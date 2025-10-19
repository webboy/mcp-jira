# Quick Start Guide

## Prerequisites
1. Python 3.10+
2. UV installed: `pipx install uv`
3. Jira Cloud account
4. API token: https://id.atlassian.com/manage-profile/security/api-tokens

## Installation

```bash
cd /home/nemanja/projects/mcp/mcp-jira
uv pip install -e .
```

## Option 1: Docker Deployment (Recommended)

### Setup
```bash
# 1. Create environment file
cp .env.example .env

# 2. Edit .env with your credentials
nano .env  # or your preferred editor

# 3. Build and start
docker compose up -d --build

# 4. Verify
curl http://localhost:9001/sse
docker logs mcp-jira
```

### Configure Cursor
Add to `~/.cursor/mcp.json`:
```json
{
  "mcpServers": {
    "jira": {
      "url": "http://localhost:9001/sse"
    }
  }
}
```

Restart Cursor and you're ready!

## Option 2: Direct UV (Development)

### Configure Cursor
Add to `~/.cursor/mcp.json`:
```json
{
  "mcpServers": {
    "jira": {
      "command": "/home/nemanja/.local/bin/uv",
      "args": ["run", "--with-editable", "/home/nemanja/projects/mcp/mcp-jira", "mcp-jira"],
      "env": {
        "JIRA_URL": "https://your-domain.atlassian.net",
        "JIRA_EMAIL": "your.email@example.com",
        "JIRA_API_TOKEN": "your_api_token_here",
        "JIRA_DEFAULT_PROJECT": "PROJ",
        "FASTMCP_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

## Testing with MCP Inspector

```bash
# Set environment variables
export JIRA_URL='https://your-domain.atlassian.net'
export JIRA_EMAIL='your.email@example.com'
export JIRA_API_TOKEN='your_api_token_here'
export JIRA_DEFAULT_PROJECT='PROJ'

# Run inspector
uv run --with mcp mcp dev src/app.py --with-editable .
```

Open the printed URL and test tools like:
- `health` - Check connectivity
- `getProjects` - List your projects
- `searchIssues` with JQL: `project = PROJ ORDER BY created DESC`

## Common Tasks

### Create an Issue
In Cursor, ask: "Create a task in project PROJ titled 'Test issue' with description 'Testing MCP integration'"

### Search Issues
In Cursor, ask: "Show me all open issues in project PROJ"

### Update an Issue
In Cursor, ask: "Update PROJ-123 to change priority to High"

### Add Comment
In Cursor, ask: "Add a comment to PROJ-123 saying 'Work in progress'"

## Troubleshooting

### Docker not starting
```bash
# Check logs
docker logs mcp-jira

# Verify .env file
cat .env

# Rebuild
docker compose down
docker compose up -d --build
```

### Connection errors
```bash
# Test Jira connectivity
curl https://your-domain.atlassian.net

# Verify credentials
# Check API token is not expired
```

### Cursor not showing tools
1. Check Docker is running: `docker ps | grep mcp-jira`
2. Verify endpoint: `curl http://localhost:9001/sse`
3. Restart Cursor completely
4. Check Cursor logs for connection errors

## Multi-Project Setup

### Project 1
```bash
cp .env.project1.example .env.project1
# Edit .env.project1
docker compose -f docker-compose.project1.yml up -d
```

### Project 2
```bash
cp .env.project2.example .env.project2
# Edit .env.project2
docker compose -f docker-compose.project2.yml up -d
```

### Cursor Config
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

## Next Steps

1. Try the health check tool in Cursor
2. List your projects
3. Search for issues
4. Create a test issue
5. Experiment with transitions and comments

See README.md for comprehensive documentation.

