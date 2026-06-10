from __future__ import annotations

from typing import Any, Callable

import requests

USER_AGENT = "dify-plugin-bugzilla/0.1.1"

Fetch = Callable[..., Any]


def api_key_headers(api_key: str | None) -> dict[str, str] | None:
    """Bugzilla REST accepts the API key via the X-BUGZILLA-API-KEY header,
    keeping the secret out of request URLs (and therefore out of error messages)."""
    if api_key:
        return {"X-BUGZILLA-API-KEY": api_key}
    return None


class BugzillaProbeError(Exception):
    pass


def check_bugzilla(base_url: str, *, api_key: str | None = None,
                   fetch: Fetch | None = None, timeout: int = 15) -> str:
    """Confirm base_url is a Bugzilla REST endpoint by reading /rest/version.
    When an api_key is supplied, also probe /rest/whoami so an invalid/expired key is
    rejected at credential-validation time instead of surfacing later at tool invoke.
    Returns the reported version string; raises BugzillaProbeError otherwise."""
    fetch = fetch or default_fetch
    base = base_url.rstrip("/")
    headers = api_key_headers(api_key)
    payload = fetch(f"{base}/rest/version", timeout, headers=headers)
    version = (payload or {}).get("version") if isinstance(payload, dict) else None
    if not version:
        raise BugzillaProbeError(
            f"{base_url} did not return a Bugzilla REST version response")
    if api_key:
        # /rest/version is unauthenticated, so it never exercises the key. /rest/whoami
        # requires authentication and returns {"error": true, ...} for a bad key.
        whoami = fetch(f"{base}/rest/whoami", timeout, headers=headers)
        if isinstance(whoami, dict) and whoami.get("error"):
            raise BugzillaProbeError(
                str(whoami.get("message") or "the supplied api_key was rejected"))
    return str(version)


def default_fetch(url: str, timeout: int = 30, *, headers: dict[str, str] | None = None) -> Any:
    request_headers = {"User-Agent": USER_AGENT}
    if headers:
        request_headers.update(headers)
    response = requests.get(url, timeout=timeout, headers=request_headers)
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
