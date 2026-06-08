from __future__ import annotations

from typing import Any
from urllib.parse import quote, urlencode

from .errors import BugNotFound
from .http import Fetch, default_fetch


def bug_browser_url(base_url: str, bug_id: str) -> str:
    return f"{base_url.rstrip('/')}/show_bug.cgi?id={quote(str(bug_id))}"


def _with_key(params: dict[str, Any], api_key: str | None) -> str:
    if api_key:
        params = {**params, "api_key": api_key}
    return urlencode(params)


def bug_url(base_url: str, bug_id: str, *, api_key: str | None = None) -> str:
    q = _with_key({}, api_key)
    base = f"{base_url.rstrip('/')}/rest/bug/{quote(str(bug_id))}"
    return f"{base}?{q}" if q else base


def comments_url(base_url: str, bug_id: str, *, api_key: str | None = None) -> str:
    q = _with_key({}, api_key)
    base = f"{base_url.rstrip('/')}/rest/bug/{quote(str(bug_id))}/comment"
    return f"{base}?{q}" if q else base


def fetch_bug(base_url: str, bug_id: str, *, api_key: str | None = None,
              fetch: Fetch = default_fetch, timeout: int = 30) -> dict[str, Any]:
    payload = fetch(bug_url(base_url, bug_id, api_key=api_key), timeout)
    if isinstance(payload, dict) and payload.get("error"):
        raise BugNotFound(str(payload.get("message") or f"Bug {bug_id} not found"))
    bugs = (payload or {}).get("bugs") or []
    if not bugs:
        raise BugNotFound(f"Bug {bug_id} not found in Bugzilla")
    return bugs[0]


def fetch_comments(base_url: str, bug_id: str, *, api_key: str | None = None,
                   fetch: Fetch = default_fetch, timeout: int = 30) -> list[dict[str, Any]]:
    payload = fetch(comments_url(base_url, bug_id, api_key=api_key), timeout)
    bugs = (payload or {}).get("bugs") or {}
    entry = bugs.get(str(bug_id)) or {}
    comments = entry.get("comments") or []
    return [c for c in comments if isinstance(c, dict)]


def status_line(bug: dict[str, Any]) -> str:
    status = str(bug.get("status") or "").strip()
    resolution = str(bug.get("resolution") or "").strip()
    return f"{status} {resolution}".strip()


def _first_lines(text: str, count: int) -> str:
    lines = [" ".join(line.split()) for line in str(text).splitlines() if line.strip()]
    return "\n".join(lines[:count])


def format_bug(bug: dict[str, Any], comments: list[dict[str, Any]], base_url: str, *,
               max_comments: int = 3, comment_lines: int = 4) -> str:
    bug_id = bug.get("id")
    summary = str(bug.get("summary") or "").strip()
    lines = [f"Bug {bug_id} [{status_line(bug)}]: {summary}"]

    product = str(bug.get("product") or "").strip()
    component = str(bug.get("component") or "").strip()
    version = str(bug.get("version") or "").strip()
    pc = "/".join(x for x in (product, component) if x)
    if pc:
        lines.append(f"Product: {pc}" + (f", version {version}" if version else ""))

    severity = str(bug.get("severity") or "").strip()
    assigned = str(bug.get("assigned_to") or "").strip()
    meta = []
    if severity:
        meta.append(f"severity: {severity}")
    if assigned:
        meta.append(f"assigned to: {assigned}")
    if meta:
        lines.append(", ".join(meta))

    lines.append(f"Link: {bug_browser_url(base_url, str(bug_id))}")

    if comments:
        lines.append("")
        lines.append(f"Comments (showing {min(len(comments), max_comments)} of {len(comments)}):")
        for comment in comments[:max_comments]:
            num = comment.get("count")
            who = str(comment.get("creator") or "").strip()
            when = str(comment.get("creation_time") or comment.get("time") or "")[:10]
            text = _first_lines(comment.get("text") or "", comment_lines)
            lines.append(f"#{num} {who} {when}:")
            if text:
                lines.append(text)
    return "\n".join(line for line in lines).strip()
