from __future__ import annotations

from typing import Any, Callable

import requests

Fetch = Callable[..., Any]


def api_key_headers(api_key: str | None) -> dict[str, str] | None:
    """Bugzilla REST accepts the API key via the X-BUGZILLA-API-KEY header,
    keeping the secret out of request URLs (and therefore out of error messages)."""
    if api_key:
        return {"X-BUGZILLA-API-KEY": api_key}
    return None


def default_fetch(url: str, timeout: int = 30, *, headers: dict[str, str] | None = None) -> Any:
    response = requests.get(url, timeout=timeout, headers=headers)
    # Modern Bugzilla (5.x, BMO) signals API errors with a real 4xx status AND a JSON
    # body {"error": true, "code": .., "message": ..}. Hand that body to the domain layer
    # so it can raise a friendly BugNotFound/BugzillaSearchError instead of a raw HTTPError.
    # Only fall back to raise_for_status() when the response is not a usable JSON object.
    try:
        payload = response.json()
    except ValueError:
        payload = None
    if isinstance(payload, dict):
        return payload
    response.raise_for_status()
    return payload
