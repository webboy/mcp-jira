# Active Context

## Current Focus

Jira MCP server enhanced with essential collaboration and user management tools. Server is production-ready and tested with real Jira Cloud instance.

Key capabilities:
- Issue lifecycle management (create, read, update, search, transition)
- Comments and attachments
- User search and management
- Worklog/time tracking
- Issue linking
- Project and metadata queries

## Recent Changes

### October 19, 2025 - Essential Tools Expansion

1. **User Search & Management**
   - Added `searchUsers` tool to find users by email/username/display name
   - Returns accountId required for issue assignments
   - Supports pagination and inactive user filtering

2. **Worklog/Time Tracking**
   - Added `addWorklog` tool for time entries (e.g., "3h 30m", "2d 4h")
   - Added `getWorklogs` tool to retrieve time logs
   - Supports optional comments and custom start times

3. **Issue Linking**
   - Added `createIssueLink` to create relationships between issues
   - Added `getIssueLinkTypes` to discover available link types (Blocks, Relates, etc.)
   - Supports optional comments on links

4. **Critical Bug Fixes**
   - Fixed `updateIssue` assignee field for Jira Cloud compatibility
   - Now auto-detects accountId format (e.g., "712020:...")
   - Falls back to name format for Jira Server

5. **Client Library Expansion**
   - Added 40+ methods to JiraClient for future tool exposure
   - Includes boards, sprints, versions, components, filters
   - Available for selective tool exposure as needed

### Initial Implementation (Earlier)

1. **Project Setup**
   - Created `pyproject.toml` with dependencies
   - Configured hatchling build system
   - Set up entry point: `mcp-jira`

2. **Core Implementation**
   - `src/config.py`: Environment-based configuration
   - `src/jira_client.py`: Wrapper around `atlassian-python-api`
   - `src/server.py`: MCP server with 18 tools for issue management
   - `src/cli.py`: CLI with stdio/SSE transport support
   - `src/app.py`: MCP Inspector support

3. **Docker Support**
   - Dockerfile with Python 3.10-slim base
   - docker-compose.yml for single instance (port 9001)
   - Multi-project configs (project1, project2)
   - Environment templates (.env.example)
   - .dockerignore for optimized builds

4. **Production Testing**
   - Successfully tested with Intelycx Jira Cloud instance
   - Created demo issue MIM-6859 via MCP tools
   - Verified user assignment with accountId resolution
   - Added AI-generated comments demonstrating functionality

## Next Steps

1. **Documentation** (Current)
   - Update README.md with new tools
   - Document accountId vs username for assignee field
   - Add examples for new tools

2. **Future Enhancements** (As needed)
   - Expose board and sprint operations as tools
   - Add version/release management tools
   - Add component management tools
   - Add filter execution tools
   - Implement bulk operations
   - Add more advanced JQL helpers
   - Support direct file path attachments (not just base64)

## Active Decisions

- **Port 9001**: Differentiate from Bitbucket MCP (9000)
- **atlassian-python-api**: Comprehensive, actively maintained library
- **Issue-focused scope**: Start with core issue operations, expand later
- **Base64 attachments**: Simple initial approach for file uploads
- **Optional fields**: Use `additional_fields` JSON string for flexibility
- **Error handling**: Consistent `{"success": bool, "data"/"error": Any}` pattern

## Known Considerations

- **JQL Complexity**: Users need to know JQL syntax for searches (could add helpers)
- **Custom Fields**: Generic approach via `additional_fields`, may need project-specific docs
- **Attachment Size**: Base64 encoding increases size ~33%, consider limits
- **API Rate Limits**: Jira Cloud has rate limits, not currently handling retry logic
- **Assignee Format**: Auto-detects accountId (Jira Cloud) vs username (Jira Server) by checking for ":" in value
- **MCP Parameter Serialization**: JSON objects in string parameters get auto-parsed by MCP client; use workarounds when needed

## Integration Points

- **Cursor**: Primary use case via MCP.json configuration
- **MCP Inspector**: Development and testing tool
- **Docker**: Production deployment method
- **Jira Cloud API v3**: Via atlassian-python-api library

