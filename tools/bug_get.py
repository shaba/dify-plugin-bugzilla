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
        except BugNotFound as exc:
            yield self.create_text_message(str(exc))
            return
        except Exception as exc:  # noqa: BLE001
            yield self.create_text_message(f"Bugzilla request error: {exc}")
            return

        # The bug exists; a comment-fetch failure (e.g. restricted comments) must not
        # discard the bug we already have. Treat it as non-fatal and append a note.
        comments: list = []
        comments_note = ""
        try:
            comments = fetch_comments(base_url, bug_id, api_key=api_key)
        except Exception as exc:  # noqa: BLE001
            comments_note = f"Comments unavailable: {exc}"

        text = format_bug(bug, comments, base_url)
        if comments_note:
            text = f"{text}\n\n{comments_note}"
        yield self.create_text_message(text)
        yield self.create_json_message({
            "id": bug.get("id"),
            "status": status_line(bug),
            "summary": bug.get("summary"),
            "url": bug_browser_url(base_url, bug_id),
        })
