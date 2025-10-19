from __future__ import annotations

import base64
import json
from typing import Any, Dict, Optional, Callable, Annotated
from pydantic import Field

import structlog
from mcp.server.fastmcp import FastMCP

from jira_client import JiraClient
from config import JiraConfig


logger = structlog.get_logger(__name__)


class JiraMcpServer:
    """MCP server and tool registry for Jira."""

    def __init__(self, config: JiraConfig) -> None:
        self._config = config
        if not (config.base_url and config.email and config.api_token):
            raise RuntimeError(
                "JIRA_URL, JIRA_EMAIL, and JIRA_API_TOKEN must be provided"
            )
        self._client = JiraClient(config)
        self._server = FastMCP(name="mcp-jira")
        self._register_tools()

    def _register_tools(self) -> None:
        s = self._server

        @s.tool()
        def health(
            check_connectivity: Annotated[bool, Field(description="If True, verify Jira connectivity by fetching server info")] = True,
        ) -> Dict[str, Any]:
            """Health check: validates configuration and Jira connectivity."""
            return self._safe(lambda: self.tool_health(check_connectivity=check_connectivity))

        @s.tool()
        def getIssue(
            issue_key: Annotated[str, Field(description="Issue key (e.g., PROJ-123)")],
            fields: Annotated[Optional[str], Field(description="Comma-separated list of fields to return")] = None,
            expand: Annotated[Optional[str], Field(description="Comma-separated list of parameters to expand")] = None,
        ) -> Dict[str, Any]:
            """Get issue details by key."""
            return self._safe(lambda: self.tool_get_issue(issue_key=issue_key, fields=fields, expand=expand))

        @s.tool()
        def createIssue(
            project: Annotated[str, Field(description="Project key (e.g., PROJ)")],
            summary: Annotated[str, Field(description="Issue summary/title")],
            description: Annotated[str, Field(description="Issue description")],
            issue_type: Annotated[str, Field(description="Issue type (e.g., Task, Bug, Story)")] = "Task",
            priority: Annotated[Optional[str], Field(description="Priority name (e.g., High, Medium, Low)")] = None,
            assignee: Annotated[Optional[str], Field(description="Assignee account ID or username")] = None,
            labels: Annotated[Optional[list[str]], Field(description="List of labels")] = None,
            additional_fields: Annotated[Optional[str], Field(description="JSON string of additional fields")] = None,
        ) -> Dict[str, Any]:
            """Create a new issue in Jira."""
            return self._safe(lambda: self.tool_create_issue(
                project=project,
                summary=summary,
                description=description,
                issue_type=issue_type,
                priority=priority,
                assignee=assignee,
                labels=labels,
                additional_fields=additional_fields,
            ))

        @s.tool()
        def updateIssue(
            issue_key: Annotated[str, Field(description="Issue key (e.g., PROJ-123)")],
            summary: Annotated[Optional[str], Field(description="New summary/title")] = None,
            description: Annotated[Optional[str], Field(description="New description")] = None,
            priority: Annotated[Optional[str], Field(description="New priority name")] = None,
            assignee: Annotated[Optional[str], Field(description="New assignee account ID or username")] = None,
            labels: Annotated[Optional[list[str]], Field(description="New list of labels (replaces existing)")] = None,
            additional_fields: Annotated[Optional[str], Field(description="JSON string of additional fields to update")] = None,
        ) -> Dict[str, Any]:
            """Update an existing issue's fields."""
            return self._safe(lambda: self.tool_update_issue(
                issue_key=issue_key,
                summary=summary,
                description=description,
                priority=priority,
                assignee=assignee,
                labels=labels,
                additional_fields=additional_fields,
            ))

        @s.tool()
        def searchIssues(
            jql: Annotated[str, Field(description="JQL query string (e.g., 'project = PROJ AND status = Open')")],
            max_results: Annotated[int, Field(description="Maximum number of issues to return", ge=1, le=100)] = 50,
            fields: Annotated[Optional[str], Field(description="Comma-separated list of fields to return")] = None,
            expand: Annotated[Optional[str], Field(description="Comma-separated list of parameters to expand")] = None,
        ) -> Dict[str, Any]:
            """Search for issues using JQL (Jira Query Language)."""
            return self._safe(lambda: self.tool_search_issues(jql=jql, max_results=max_results, fields=fields, expand=expand))

        @s.tool()
        def getTransitions(
            issue_key: Annotated[str, Field(description="Issue key (e.g., PROJ-123)")],
        ) -> Dict[str, Any]:
            """Get available transitions (status changes) for an issue."""
            return self._safe(lambda: self.tool_get_transitions(issue_key=issue_key))

        @s.tool()
        def transitionIssue(
            issue_key: Annotated[str, Field(description="Issue key (e.g., PROJ-123)")],
            transition_id: Annotated[str, Field(description="Transition ID (get from getTransitions)")],
            comment: Annotated[Optional[str], Field(description="Optional comment to add with transition")] = None,
            additional_fields: Annotated[Optional[str], Field(description="JSON string of additional fields required by transition")] = None,
        ) -> Dict[str, Any]:
            """Transition an issue to a new status."""
            return self._safe(lambda: self.tool_transition_issue(
                issue_key=issue_key,
                transition_id=transition_id,
                comment=comment,
                additional_fields=additional_fields,
            ))

        @s.tool()
        def addComment(
            issue_key: Annotated[str, Field(description="Issue key (e.g., PROJ-123)")],
            comment: Annotated[str, Field(description="Comment text to add")],
        ) -> Dict[str, Any]:
            """Add a comment to an issue."""
            return self._safe(lambda: self.tool_add_comment(issue_key=issue_key, comment=comment))

        @s.tool()
        def getComments(
            issue_key: Annotated[str, Field(description="Issue key (e.g., PROJ-123)")],
        ) -> Dict[str, Any]:
            """Get all comments for an issue."""
            return self._safe(lambda: self.tool_get_comments(issue_key=issue_key))

        @s.tool()
        def addAttachment(
            issue_key: Annotated[str, Field(description="Issue key (e.g., PROJ-123)")],
            filename: Annotated[str, Field(description="Name of the file to attach")],
            content_base64: Annotated[str, Field(description="Base64-encoded file content")],
        ) -> Dict[str, Any]:
            """Add an attachment to an issue."""
            return self._safe(lambda: self.tool_add_attachment(
                issue_key=issue_key,
                filename=filename,
                content_base64=content_base64,
            ))

        @s.tool()
        def getProjects(
            limit: Annotated[int, Field(description="Maximum number of projects to return", ge=1, le=100)] = 50,
        ) -> Dict[str, Any]:
            """List all accessible projects."""
            return self._safe(lambda: self.tool_get_projects(limit=limit))

        @s.tool()
        def getProject(
            project_key: Annotated[str, Field(description="Project key (e.g., PROJ)")],
        ) -> Dict[str, Any]:
            """Get detailed information about a specific project."""
            return self._safe(lambda: self.tool_get_project(project_key=project_key))

        @s.tool()
        def getIssueTypes(
            project_key: Annotated[Optional[str], Field(description="Project key to get issue types for (optional)")] = None,
        ) -> Dict[str, Any]:
            """Get issue types for a project or all issue types."""
            return self._safe(lambda: self.tool_get_issue_types(project_key=project_key))

        @s.tool()
        def searchUsers(
            query: Annotated[str, Field(description="Search query (email, username, or display name)")],
            max_results: Annotated[int, Field(description="Maximum number of users to return", ge=1, le=100)] = 50,
            include_inactive: Annotated[bool, Field(description="Include inactive users in results")] = False,
        ) -> Dict[str, Any]:
            """Search for users by email, username, or display name. Returns accountId needed for assignments."""
            return self._safe(lambda: self.tool_search_users(
                query=query,
                max_results=max_results,
                include_inactive=include_inactive,
            ))

        @s.tool()
        def addWorklog(
            issue_key: Annotated[str, Field(description="Issue key (e.g., PROJ-123)")],
            time_spent: Annotated[str, Field(description="Time spent (e.g., '3h 30m', '2d 4h', '1w 2d')")],
            comment: Annotated[Optional[str], Field(description="Optional worklog comment")] = None,
            started: Annotated[Optional[str], Field(description="When work started (ISO 8601 format, e.g., '2024-01-15T09:00:00.000+0000')")] = None,
        ) -> Dict[str, Any]:
            """Add a worklog (time tracking) entry to an issue."""
            return self._safe(lambda: self.tool_add_worklog(
                issue_key=issue_key,
                time_spent=time_spent,
                comment=comment,
                started=started,
            ))

        @s.tool()
        def getWorklogs(
            issue_key: Annotated[str, Field(description="Issue key (e.g., PROJ-123)")],
        ) -> Dict[str, Any]:
            """Get all worklog entries for an issue."""
            return self._safe(lambda: self.tool_get_worklogs(issue_key=issue_key))

        @s.tool()
        def createIssueLink(
            link_type: Annotated[str, Field(description="Link type name (e.g., 'Blocks', 'Relates')")],
            inward_issue: Annotated[str, Field(description="Inward issue key (e.g., PROJ-123)")],
            outward_issue: Annotated[str, Field(description="Outward issue key (e.g., PROJ-456)")],
            comment: Annotated[Optional[str], Field(description="Optional comment for the link")] = None,
        ) -> Dict[str, Any]:
            """Create a link between two issues. Use getIssueLinkTypes to see available link types."""
            return self._safe(lambda: self.tool_create_issue_link(
                link_type=link_type,
                inward_issue=inward_issue,
                outward_issue=outward_issue,
                comment=comment,
            ))

        @s.tool()
        def getIssueLinkTypes(
        ) -> Dict[str, Any]:
            """Get available issue link types (e.g., 'Blocks', 'Relates', 'Duplicates')."""
            return self._safe(lambda: self.tool_get_issue_link_types())

    def _safe(self, fn: Callable[[], Any]) -> Dict[str, Any]:
        """Execute a function and return a formatted response."""
        try:
            result = fn()
            return {
                "success": True,
                "data": result,
            }
        except Exception as e:
            logger.error("Tool execution failed", error=str(e), exc_info=True)
            return {
                "success": False,
                "error": str(e),
            }

    # ---------- Tool implementations ----------
    def tool_health(self, check_connectivity: bool) -> Dict[str, Any]:
        """Health check implementation."""
        config_status = {
            "jira_url": self._config.base_url,
            "jira_email": self._config.email,
            "api_token_configured": bool(self._config.api_token),
            "default_project": self._config.default_project,
        }
        
        if check_connectivity:
            health = self._client.health_check()
            return {
                "config": config_status,
                "connectivity": health,
            }
        else:
            return {
                "config": config_status,
                "connectivity": "not_checked",
            }

    def tool_get_issue(self, issue_key: str, fields: Optional[str], expand: Optional[str]) -> Any:
        """Get issue implementation."""
        return self._client.get_issue(issue_key, fields=fields, expand=expand)

    def tool_create_issue(
        self,
        project: str,
        summary: str,
        description: str,
        issue_type: str,
        priority: Optional[str],
        assignee: Optional[str],
        labels: Optional[list[str]],
        additional_fields: Optional[str],
    ) -> Any:
        """Create issue implementation."""
        fields: Dict[str, Any] = {}
        
        if priority:
            fields["priority"] = {"name": priority}
        
        if assignee:
            fields["assignee"] = {"name": assignee}
        
        if labels:
            fields["labels"] = labels
        
        if additional_fields:
            try:
                extra = json.loads(additional_fields)
                fields.update(extra)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON in additional_fields: {e}")
        
        return self._client.create_issue(
            project=project,
            summary=summary,
            description=description,
            issue_type=issue_type,
            fields=fields if fields else None,
        )

    def tool_update_issue(
        self,
        issue_key: str,
        summary: Optional[str],
        description: Optional[str],
        priority: Optional[str],
        assignee: Optional[str],
        labels: Optional[list[str]],
        additional_fields: Optional[str],
    ) -> Any:
        """Update issue implementation."""
        fields: Dict[str, Any] = {}
        
        if summary:
            fields["summary"] = summary
        
        if description:
            fields["description"] = description
        
        if priority:
            fields["priority"] = {"name": priority}
        
        if assignee:
            # For Jira Cloud, use accountId. For Jira Server, use name.
            # accountId format: "712020:af6d11d4-1824-4a43-97e4-964ba3318f82"
            if ":" in assignee:  # Likely an accountId
                fields["assignee"] = {"accountId": assignee}
            else:  # Likely a username (for Jira Server)
                fields["assignee"] = {"name": assignee}
        
        if labels is not None:
            fields["labels"] = labels
        
        if additional_fields:
            try:
                extra = json.loads(additional_fields)
                fields.update(extra)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON in additional_fields: {e}")
        
        if not fields:
            raise ValueError("At least one field must be provided for update")
        
        return self._client.update_issue(issue_key, fields)

    def tool_search_issues(self, jql: str, max_results: int, fields: Optional[str], expand: Optional[str]) -> Any:
        """Search issues implementation."""
        return self._client.search_issues(jql, max_results=max_results, fields=fields, expand=expand)

    def tool_get_transitions(self, issue_key: str) -> List[Dict[str, Any]]:
        """Get transitions implementation."""
        return self._client.get_transitions(issue_key)

    def tool_transition_issue(
        self,
        issue_key: str,
        transition_id: str,
        comment: Optional[str],
        additional_fields: Optional[str],
    ) -> Any:
        """Transition issue implementation."""
        fields = None
        if additional_fields:
            try:
                fields = json.loads(additional_fields)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON in additional_fields: {e}")
        
        return self._client.transition_issue(
            issue_key=issue_key,
            transition_id=transition_id,
            fields=fields,
            comment=comment,
        )

    def tool_add_comment(self, issue_key: str, comment: str) -> Any:
        """Add comment implementation."""
        return self._client.add_comment(issue_key, comment)

    def tool_get_comments(self, issue_key: str) -> List[Dict[str, Any]]:
        """Get comments implementation."""
        return self._client.get_comments(issue_key)

    def tool_add_attachment(self, issue_key: str, filename: str, content_base64: str) -> Any:
        """Add attachment implementation."""
        try:
            content = base64.b64decode(content_base64)
        except Exception as e:
            raise ValueError(f"Invalid base64 content: {e}")
        
        return self._client.add_attachment(issue_key, filename, content)

    def tool_get_projects(self, limit: int) -> List[Dict[str, Any]]:
        """Get projects implementation."""
        projects = self._client.get_projects()
        return projects[:limit]

    def tool_get_project(self, project_key: str) -> Any:
        """Get project implementation."""
        return self._client.get_project(project_key)

    def tool_get_issue_types(self, project_key: Optional[str]) -> List[Dict[str, Any]]:
        """Get issue types implementation."""
        return self._client.get_issue_types(project_key)

    def tool_search_users(
        self,
        query: str,
        max_results: int,
        include_inactive: bool,
    ) -> List[Dict[str, Any]]:
        """Search users implementation."""
        return self._client.search_users(
            query=query,
            limit=max_results,
            include_inactive=include_inactive,
        )

    def tool_add_worklog(
        self,
        issue_key: str,
        time_spent: str,
        comment: Optional[str],
        started: Optional[str],
    ) -> Dict[str, Any]:
        """Add worklog implementation."""
        return self._client.add_worklog(
            issue_key=issue_key,
            time_spent=time_spent,
            comment=comment,
            started=started,
        )

    def tool_get_worklogs(self, issue_key: str) -> List[Dict[str, Any]]:
        """Get worklogs implementation."""
        return self._client.get_issue_worklogs(issue_key)

    def tool_create_issue_link(
        self,
        link_type: str,
        inward_issue: str,
        outward_issue: str,
        comment: Optional[str],
    ) -> Any:
        """Create issue link implementation."""
        return self._client.create_issue_link(
            link_type=link_type,
            inward_issue=inward_issue,
            outward_issue=outward_issue,
            comment=comment,
        )

    def tool_get_issue_link_types(self) -> List[Dict[str, Any]]:
        """Get issue link types implementation."""
        return self._client.get_issue_link_types()

    # ---------- Transport methods ----------
    async def run_stdio(self) -> None:
        """Run the server using stdio transport."""
        await self._server.run_stdio_async()

    async def run_sse(self, host: str = "0.0.0.0", port: int = 9001) -> None:
        """Run server with SSE (HTTP) transport."""
        from mcp.server.sse import SseServerTransport
        import uvicorn

        sse = SseServerTransport("/messages")

        async def app(scope, receive, send):
            """ASGI application that routes SSE requests."""
            if scope["type"] == "http":
                path = scope["path"]
                method = scope["method"]
                
                if path == "/sse" and method == "GET":
                    # Handle SSE connection
                    async with sse.connect_sse(scope, receive, send) as streams:
                        await self._server._mcp_server.run(
                            streams[0], streams[1], self._server._mcp_server.create_initialization_options()
                        )
                elif path == "/messages" and method == "POST":
                    # Handle POST messages
                    await sse.handle_post_message(scope, receive, send)
                else:
                    # 404 for other paths
                    await send({
                        "type": "http.response.start",
                        "status": 404,
                        "headers": [[b"content-type", b"text/plain"]],
                    })
                    await send({
                        "type": "http.response.body",
                        "body": b"Not Found",
                    })

        config = uvicorn.Config(app, host=host, port=port, log_level="info")
        server = uvicorn.Server(config)
        await server.serve()

