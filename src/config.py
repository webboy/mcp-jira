from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class JiraConfig:
    base_url: str
    email: str
    api_token: str
    default_project: Optional[str]


def load_config_from_env() -> JiraConfig:
    return JiraConfig(
        base_url=os.environ.get("JIRA_URL", ""),
        email=os.environ.get("JIRA_EMAIL", ""),
        api_token=os.environ.get("JIRA_API_TOKEN", ""),
        default_project=os.environ.get("JIRA_DEFAULT_PROJECT"),
    )

