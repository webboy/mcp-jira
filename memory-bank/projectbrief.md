# Project Brief

Build a Python MCP server for Jira Cloud API, mirroring the architecture of the existing Bitbucket MCP server. Use a `src` layout and manage the project with UV. The server should expose tools for issue management including CRUD operations, search, transitions, comments, and attachments.

## Key Requirements

- **Architecture**: Mirror `/home/nemanja/projects/mcp/mcp-bitbucket` structure
- **SDK**: Use `atlassian-python-api` library for Jira integration
- **Transport**: Support both stdio (development) and HTTP/SSE (Docker deployment)
- **Port**: Default to 9001 (vs Bitbucket's 9000)
- **Authentication**: Email + API Token (Jira Cloud standard)
- **Scope**: Issue management operations (not boards/sprints in initial version)

## Core Features

### Issue Operations
- Get issue details
- Create new issues
- Update existing issues
- Search issues with JQL
- Get available transitions
- Transition issues to different statuses
- Add comments
- Get comments
- Add attachments

### Helper Operations
- Health check
- List projects
- Get project details
- Get issue types

## Technical Stack

- Python 3.10+
- UV for dependency management
- FastMCP for MCP server
- atlassian-python-api for Jira API
- Docker with HTTP/SSE transport
- Structlog for logging

