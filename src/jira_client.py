from __future__ import annotations

import base64
from typing import Any, Dict, List, Optional

import structlog
from atlassian import Jira

from config import JiraConfig


logger = structlog.get_logger(__name__)


class JiraClient:
    """Wrapper around atlassian-python-api's Jira client.
    
    Provides methods for issue operations: get, create, update, search, 
    transitions, comments, and attachments.
    """

    def __init__(self, config: JiraConfig) -> None:
        self._config = config
        if not config.base_url or not config.email or not config.api_token:
            raise RuntimeError(
                "JIRA_URL, JIRA_EMAIL, and JIRA_API_TOKEN must be provided"
            )
        
        self._client = Jira(
            url=config.base_url,
            username=config.email,
            password=config.api_token,
            cloud=True,
        )

    # ---------- Issue operations ----------
    def get_issue(self, issue_key: str, fields: Optional[str] = None, expand: Optional[str] = None) -> Any:
        """Get issue details by key."""
        return self._client.issue(issue_key, fields=fields, expand=expand)

    def create_issue(
        self,
        project: str,
        summary: str,
        description: str,
        issue_type: str,
        fields: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Create a new issue."""
        issue_fields = {
            "project": {"key": project},
            "summary": summary,
            "description": description,
            "issuetype": {"name": issue_type},
        }
        
        if fields:
            issue_fields.update(fields)
        
        return self._client.create_issue(fields=issue_fields)

    def update_issue(self, issue_key: str, fields: Dict[str, Any]) -> Any:
        """Update issue fields."""
        return self._client.update_issue_field(issue_key, fields)

    def search_issues(
        self,
        jql: str,
        max_results: int = 50,
        fields: Optional[str] = None,
        expand: Optional[str] = None,
    ) -> Any:
        """Search issues using JQL."""
        return self._client.jql(jql, limit=max_results, fields=fields, expand=expand)

    # ---------- Transition operations ----------
    def get_transitions(self, issue_key: str) -> List[Dict[str, Any]]:
        """Get available transitions for an issue."""
        result = self._client.get_issue_transitions(issue_key)
        # atlassian-python-api returns a list directly, not a dict
        if isinstance(result, list):
            return result
        # Fallback for dict format (older versions or different endpoints)
        return result.get("transitions", []) if isinstance(result, dict) else []

    def transition_issue(
        self,
        issue_key: str,
        transition_id: str,
        fields: Optional[Dict[str, Any]] = None,
        comment: Optional[str] = None,
    ) -> Any:
        """Transition an issue to a new status."""
        # Build transition payload
        transition_data = {"transition": {"id": transition_id}}
        
        # Add fields if provided
        if fields:
            transition_data["fields"] = fields
        
        # Add comment if provided
        if comment:
            transition_data["update"] = {
                "comment": [
                    {
                        "add": {
                            "body": comment
                        }
                    }
                ]
            }
        
        # Use the REST API method directly
        url = f"rest/api/3/issue/{issue_key}/transitions"
        result = self._client.post(url, data=transition_data)
        
        return result

    # ---------- Comment operations ----------
    def add_comment(self, issue_key: str, comment: str) -> Any:
        """Add a comment to an issue."""
        return self._client.issue_add_comment(issue_key, comment)

    def get_comments(self, issue_key: str) -> List[Dict[str, Any]]:
        """Get all comments for an issue."""
        result = self._client.issue_get_comments(issue_key)
        return result.get("comments", [])

    # ---------- Attachment operations ----------
    def add_attachment(self, issue_key: str, filename: str, content: bytes) -> Any:
        """Add an attachment to an issue."""
        # The atlassian library expects file-like object or path
        # For now, we'll use a simple approach with the library's method
        import io
        file_obj = io.BytesIO(content)
        file_obj.name = filename
        return self._client.add_attachment(issue_key, attachment=file_obj)

    # ---------- Helper operations ----------
    def get_projects(self) -> List[Dict[str, Any]]:
        """Get all accessible projects."""
        return self._client.projects(included_archived=False)

    def get_issue_types(self, project_key: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get issue types for a project or all issue types."""
        if project_key:
            project = self._client.project(project_key)
            return project.get("issueTypes", [])
        else:
            return self._client.get_all_issue_types()

    def get_project(self, project_key: str) -> Any:
        """Get project details."""
        return self._client.project(project_key)

    def health_check(self) -> Dict[str, Any]:
        """Perform a health check by getting server info."""
        try:
            info = self._client.get_server_info()
            return {
                "status": "ok",
                "server_info": info
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    # ---------- User operations ----------
    def search_users(
        self,
        query: str,
        start: int = 0,
        limit: int = 50,
        include_inactive: bool = False,
    ) -> List[Dict[str, Any]]:
        """Search for users by email, username, or display name."""
        result = self._client.user_find_by_user_string(
            query=query,
            start=start,
            limit=limit,
            include_inactive_users=include_inactive,
            include_active_users=True,
        )
        # Ensure we return a list
        if isinstance(result, list):
            return result
        return []

    def get_user(self, account_id: str) -> Dict[str, Any]:
        """Get user details by account ID."""
        return self._client.user(account_id=account_id)

    def get_assignable_users_for_issue(
        self,
        issue_key: str,
        start: int = 0,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Get users that can be assigned to a specific issue."""
        result = self._client.get_assignable_users_for_issue(
            issue_key=issue_key,
            start=start,
            limit=limit,
        )
        return result if isinstance(result, list) else []

    def get_assignable_users_for_project(
        self,
        project_key: str,
        start: int = 0,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Get users that can be assigned to issues in a project."""
        result = self._client.get_all_assignable_users_for_project(
            project_key=project_key,
            start=start,
            limit=limit,
        )
        return result if isinstance(result, list) else []

    # ---------- Board operations ----------
    def get_boards(
        self,
        start: int = 0,
        limit: int = 50,
        project_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get all agile boards, optionally filtered by project."""
        params = {"startAt": start, "maxResults": limit}
        if project_key:
            params["projectKeyOrId"] = project_key
        return self._client.get_all_agile_boards(start=start, limit=limit, project_key_or_id=project_key)

    def get_board(self, board_id: int) -> Dict[str, Any]:
        """Get details of a specific board."""
        return self._client.get_agile_board(board_id)

    def get_board_issues(
        self,
        board_id: int,
        start: int = 0,
        limit: int = 50,
        jql: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get issues for a board, optionally filtered by JQL."""
        return self._client.get_issues_for_board(
            board_id=board_id,
            start=start,
            limit=limit,
            jql=jql,
        )

    # ---------- Sprint operations ----------
    def get_sprints(
        self,
        board_id: int,
        start: int = 0,
        limit: int = 50,
        state: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get sprints for a board. State can be: active, closed, future."""
        return self._client.get_all_sprint(
            board_id=board_id,
            start=start,
            limit=limit,
            state=state,
        )

    def get_sprint(self, sprint_id: int) -> Dict[str, Any]:
        """Get details of a specific sprint."""
        return self._client.get_sprint(sprint_id)

    def get_sprint_issues(
        self,
        sprint_id: int,
        start: int = 0,
        limit: int = 50,
        jql: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get issues in a sprint."""
        return self._client.get_sprint_issues(
            sprint_id=sprint_id,
            start=start,
            limit=limit,
            jql=jql,
        )

    def move_issues_to_sprint(self, sprint_id: int, issue_keys: List[str]) -> Any:
        """Move issues to a sprint."""
        return self._client.add_issues_to_sprint(sprint_id, issue_keys)

    # ---------- Worklog operations ----------
    def add_worklog(
        self,
        issue_key: str,
        time_spent: str,
        comment: Optional[str] = None,
        started: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add a worklog entry to an issue. Time format: '3h 30m' or '2d 4h'."""
        return self._client.add_worklog(
            issue=issue_key,
            timeSpent=time_spent,
            comment=comment,
            started=started,
        )

    def get_issue_worklogs(self, issue_key: str) -> List[Dict[str, Any]]:
        """Get all worklogs for an issue."""
        result = self._client.issue_worklog(issue_key)
        return result.get("worklogs", []) if isinstance(result, dict) else []

    # ---------- Issue Link operations ----------
    def create_issue_link(
        self,
        link_type: str,
        inward_issue: str,
        outward_issue: str,
        comment: Optional[str] = None,
    ) -> Any:
        """Create a link between two issues."""
        return self._client.create_issue_link(
            inward_issue=inward_issue,
            outward_issue=outward_issue,
            link_type=link_type,
            comment=comment,
        )

    def get_issue_link_types(self) -> List[Dict[str, Any]]:
        """Get available issue link types."""
        result = self._client.get_issue_link_types()
        return result.get("issueLinkTypes", []) if isinstance(result, dict) else []

    # ---------- Version operations ----------
    def get_project_versions(self, project_key: str) -> List[Dict[str, Any]]:
        """Get all versions for a project."""
        return self._client.get_project_versions(project_key)

    def create_version(
        self,
        project_key: str,
        name: str,
        description: Optional[str] = None,
        start_date: Optional[str] = None,
        release_date: Optional[str] = None,
        archived: bool = False,
        released: bool = False,
    ) -> Dict[str, Any]:
        """Create a new version/release."""
        return self._client.add_version(
            project_key=project_key,
            version_name=name,
            description=description,
            start_date=start_date,
            release_date=release_date,
            archived=archived,
            released=released,
        )

    def update_version(
        self,
        version_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        archived: Optional[bool] = None,
        released: Optional[bool] = None,
        release_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update a version."""
        return self._client.update_version(
            version_id=version_id,
            name=name,
            description=description,
            archived=archived,
            released=released,
            release_date=release_date,
        )

    # ---------- Component operations ----------
    def get_project_components(self, project_key: str) -> List[Dict[str, Any]]:
        """Get all components for a project."""
        return self._client.get_project_components(project_key)

    def create_component(
        self,
        project_key: str,
        name: str,
        description: Optional[str] = None,
        lead_account_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new component."""
        return self._client.create_component(
            component_name=name,
            project=project_key,
            description=description,
            lead_account_id=lead_account_id,
        )

    # ---------- Filter operations ----------
    def get_my_filters(self) -> List[Dict[str, Any]]:
        """Get filters owned by the current user."""
        return self._client.get_my_filters()

    def get_favourite_filters(self) -> List[Dict[str, Any]]:
        """Get favourite filters."""
        return self._client.get_favourite_filters()

    def execute_filter(self, filter_id: int, start: int = 0, limit: int = 50) -> Dict[str, Any]:
        """Execute a saved filter and return issues."""
        return self._client.get_filter_issues(
            filter_id=filter_id,
            start=start,
            limit=limit,
        )

