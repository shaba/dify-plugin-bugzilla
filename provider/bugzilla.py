from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

from bugzilla_client.search import search_bugs


class BugzillaProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        base_url = str(credentials.get("base_url") or "").strip().rstrip("/")
        api_key = str(credentials.get("api_key") or "").strip() or None
        if not base_url:
            raise ToolProviderCredentialValidationError(
                "base_url is required (e.g. https://example.com)")
        try:
            search_bugs(base_url, "test", limit=1, api_key=api_key, timeout=15)
        except Exception as exc:  # noqa: BLE001
            raise ToolProviderCredentialValidationError(
                f"Bugzilla is not reachable at {base_url}: {exc}") from exc
