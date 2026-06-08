from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from bugzilla_client.search import format_search, search_bugs


class BugSearchTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        base_url = str(self.runtime.credentials.get("base_url") or "").strip().rstrip("/")
        api_key = str(self.runtime.credentials.get("api_key") or "").strip() or None
        query = str(tool_parameters.get("query") or "").strip()

        if not base_url:
            yield self.create_text_message("Error: the plugin base_url is not configured")
            return
        if not query:
            yield self.create_text_message("Error: the 'query' parameter is required")
            return

        try:
            bugs = search_bugs(base_url, query, limit=20, api_key=api_key)
        except Exception as exc:  # noqa: BLE001
            yield self.create_text_message(f"Bugzilla request error: {exc}")
            return

        yield self.create_text_message(format_search(bugs, query))
        yield self.create_json_message({"query": query, "count": len(bugs)})
