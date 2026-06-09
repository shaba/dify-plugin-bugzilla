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
    response.raise_for_status()
    return response.json()
