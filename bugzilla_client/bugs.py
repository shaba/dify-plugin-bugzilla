from __future__ import annotations

from typing import Any
from urllib.parse import quote

from .errors import BugNotFound, BugzillaAuthError
from .http import Fetch, api_key_headers, default_fetch


def bug_browser_url(base_url: str, bug_id: str) -> str:
    return f"{base_url.rstrip('/')}/show_bug.cgi?id={quote(str(bug_id), safe='')}"


def bug_url(base_url: str, bug_id: str) -> str:
    return f"{base_url.rstrip('/')}/rest/bug/{quote(str(bug_id), safe='')}"


def comments_url(base_url: str, bug_id: str) -> str:
    return f"{base_url.rstrip('/')}/rest/bug/{quote(str(bug_id), safe='')}/comment"


def fetch_bug(base_url: str, bug_id: str, *, api_key: str | None = None,
              fetch: Fetch = default_fetch, timeout: int = 30) -> dict[str, Any]:
    payload = fetch(bug_url(base_url, bug_id), timeout, headers=api_key_headers(api_key))
    if isinstance(payload, dict) and payload.get("error"):
        raise BugNotFound(str(payload.get("message") or f"Bug {bug_id} not found"))
    bugs = payload.get("bugs") if isinstance(payload, dict) else None
    if not bugs:
        raise BugNotFound(f"Bug {bug_id} not found in Bugzilla")
    return bugs[0]


def fetch_comments(base_url: str, bug_id: str, *, api_key: str | None = None,
                   fetch: Fetch = default_fetch, timeout: int = 30) -> list[dict[str, Any]]:
    payload = fetch(comments_url(base_url, bug_id), timeout, headers=api_key_headers(api_key))
    if isinstance(payload, dict) and payload.get("error"):
        # The comment endpoint failing is almost always a permission rejection (private
        # bug / restricted comments), not a missing bug. Keep it distinct so the bug_get
        # tool can still render the bug it already fetched.
        raise BugzillaAuthError(
            str(payload.get("message") or f"Comments for bug {bug_id} are not available"))
    bugs = payload.get("bugs") if isinstance(payload, dict) else None
    bugs = bugs if isinstance(bugs, dict) else {}
    entry = bugs.get(str(bug_id))
    if not isinstance(entry, dict) and len(bugs) == 1:
        # The response keys the map by the canonical numeric id; if the user-supplied id
        # form (leading zeros, alias) does not match but exactly one bug came back, use it.
        entry = next(iter(bugs.values()))
    entry = entry if isinstance(entry, dict) else {}
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
            marker = f"#{num} " if num is not None else ""
            lines.append(f"{marker}{who} {when}:")
            if text:
                lines.append(text)
    return "\n".join(line for line in lines).strip()
