from __future__ import annotations

from typing import Any
from urllib.parse import urlencode

from .http import Fetch, default_fetch

_SEARCH_FIELDS = "id,summary,status,resolution,product,component,severity,last_change_time"


def quicksearch_url(base_url: str, query: str, *, limit: int = 20, api_key: str | None = None) -> str:
    params: dict[str, Any] = {"quicksearch": query, "limit": limit, "include_fields": _SEARCH_FIELDS}
    if api_key:
        params["api_key"] = api_key
    return f"{base_url.rstrip('/')}/rest/bug?{urlencode(params)}"


def search_bugs(base_url: str, query: str, *, limit: int = 20, api_key: str | None = None,
                fetch: Fetch = default_fetch, timeout: int = 30) -> list[dict[str, Any]]:
    payload = fetch(quicksearch_url(base_url, query, limit=limit, api_key=api_key), timeout)
    bugs = (payload or {}).get("bugs") or []
    return [b for b in bugs if isinstance(b, dict)]


def format_search(bugs: list[dict[str, Any]], query: str, *, limit: int = 15) -> str:
    if not bugs:
        return f"No bugs found for \"{query}\"."
    shown = bugs[:limit]
    lines = [f"Found {len(bugs)} bug(s) for \"{query}\" (showing {len(shown)}):"]
    for bug in shown:
        bug_id = bug.get("id")
        status = str(bug.get("status") or "").strip()
        resolution = str(bug.get("resolution") or "").strip()
        st = f"{status} {resolution}".strip()
        summary = str(bug.get("summary") or "").strip()
        product = str(bug.get("product") or "").strip()
        component = str(bug.get("component") or "").strip()
        pc = "/".join(x for x in (product, component) if x)
        line = f"- {bug_id} [{st}]: {summary}"
        if pc:
            line += f" ({pc})"
        lines.append(line)
    return "\n".join(lines)
