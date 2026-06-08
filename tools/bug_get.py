from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from bugzilla_client.bugs import (
    bug_browser_url,
    fetch_bug,
    fetch_comments,
    format_bug,
    status_line,
)
from bugzilla_client.errors import BugNotFound


class BugGetTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        base_url = str(self.runtime.credentials.get("base_url") or "").strip().rstrip("/")
        api_key = str(self.runtime.credentials.get("api_key") or "").strip() or None
        bug_id = str(tool_parameters.get("bug_id") or "").strip()

        if not base_url:
            yield self.create_text_message("Error: the plugin base_url is not configured")
            return
        if not bug_id:
            yield self.create_text_message("Error: the 'bug_id' parameter is required")
            return

        try:
            bug = fetch_bug(base_url, bug_id, api_key=api_key)
            comments = fetch_comments(base_url, bug_id, api_key=api_key)
        except BugNotFound as exc:
            yield self.create_text_message(str(exc))
            return
        except Exception as exc:  # noqa: BLE001
            yield self.create_text_message(f"Bugzilla request error: {exc}")
            return

        yield self.create_text_message(format_bug(bug, comments, base_url))
        yield self.create_json_message({
            "id": bug.get("id"),
            "status": status_line(bug),
            "summary": bug.get("summary"),
            "url": bug_browser_url(base_url, bug_id),
        })
