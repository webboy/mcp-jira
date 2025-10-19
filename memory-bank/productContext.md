# Product Context

## Problem Statement

AI assistants like Claude (in Cursor) need programmatic access to Jira to help developers and project managers with issue tracking and project management tasks. Without MCP integration, users must manually switch between their IDE and Jira UI, breaking flow and reducing productivity.

## Solution

An MCP server that exposes Jira Cloud API operations as tools that AI assistants can invoke. This enables:

- Creating and updating issues without leaving the IDE
- Searching for issues using natural language (converted to JQL)
- Transitioning issues through workflows
- Adding comments and context to issues
- Tracking project progress and status

## Use Cases

### Developer Workflow
- "Create a bug report for the authentication issue I just found"
- "Update PROJ-123 to mark it as in progress and assign to me"
- "Add a comment to PROJ-456 with my findings"
- "Search for all high-priority bugs in my current sprint"

### Project Management
- "Show me all open tasks in the MOBILE project"
- "Transition PROJ-789 to done and add a completion comment"
- "List all issues assigned to John in the last week"
- "Create a story for the new feature with acceptance criteria"

### Team Collaboration
- "Find all issues that mention 'authentication'"
- "Show me issues that are blocked"
- "Add implementation notes to PROJ-234"

## User Experience Goals

1. **Simplicity**: Environment-based configuration, no complex setup
2. **Reliability**: Clear error messages, health checks
3. **Flexibility**: Works with any Jira Cloud instance
4. **Performance**: Fast responses via caching and efficient API usage
5. **Security**: API tokens managed securely via environment variables

## Success Criteria

- AI can successfully create, read, update, and search issues
- Works seamlessly in Cursor via Docker deployment
- Clear documentation enables quick setup (< 5 minutes)
- Supports multi-project workflows
- Handles errors gracefully with helpful messages

