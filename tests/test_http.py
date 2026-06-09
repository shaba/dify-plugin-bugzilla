"""Transport-layer tests for default_fetch and the credential probe.

These exercise the only code paths where raise_for_status() and Response.json()
actually run, including the real-world case of a 4xx HTTP status carrying a JSON
error body (modern Bugzilla 5.x / BMO), which the domain layer must see verbatim.
"""
import pytest
import requests

from bugzilla_client import http
from bugzilla_client.bugs import fetch_bug
from bugzilla_client.errors import BugNotFound
from bugzilla_client.http import BugzillaProbeError, check_bugzilla, default_fetch


class FakeResponse:
    def __init__(self, status_code, json_body, *, text="{}"):
        self.status_code = status_code
        self._json = json_body
        self.text = text

    def json(self):
        if isinstance(self._json, Exception):
            raise self._json
        return self._json

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} Client Error")


@pytest.fixture
def fake_get(monkeypatch):
    holder = {}

    def install(response):
        holder["captured"] = {}

        def _get(url, timeout=None, headers=None):
            holder["captured"]["url"] = url
            holder["captured"]["headers"] = headers
            return response

        monkeypatch.setattr(http.requests, "get", _get)
        return holder["captured"]

    return install


def test_default_fetch_returns_json_object(fake_get):
    fake_get(FakeResponse(200, {"bugs": [{"id": 1}]}))
    payload = default_fetch("https://example.com/rest/bug/1")
    assert payload == {"bugs": [{"id": 1}]}


def test_default_fetch_returns_error_body_on_4xx(fake_get):
    # 401 + JSON error body: must be returned, NOT raised, so the domain layer can map it.
    fake_get(FakeResponse(401, {"error": True, "code": 102, "message": "Access denied"}))
    payload = default_fetch("https://example.com/rest/bug/123")
    assert payload == {"error": True, "code": 102, "message": "Access denied"}


def test_default_fetch_4xx_error_body_yields_bugnotfound(fake_get):
    # End-to-end: a real 4xx with an error body surfaces the friendly BugNotFound message,
    # not a raw HTTPError.
    fake_get(FakeResponse(404, {"error": True, "message": "Bug 123 does not exist"}))
    with pytest.raises(BugNotFound) as excinfo:
        fetch_bug("https://example.com", "123")
    assert "does not exist" in str(excinfo.value)


def test_default_fetch_raises_on_non_json_4xx(fake_get):
    # No usable JSON body (e.g. an HTML 502 from a proxy): fall back to raise_for_status.
    fake_get(FakeResponse(502, ValueError("no json"), text="<html>bad gateway</html>"))
    with pytest.raises(requests.HTTPError):
        default_fetch("https://example.com/rest/bug/1")


def test_check_bugzilla_rejects_bad_api_key(fake_get):
    responses = iter([
        FakeResponse(200, {"version": "5.0.4"}),            # /rest/version
        FakeResponse(401, {"error": True, "message": "invalid api key"}),  # /rest/whoami
    ])
    fetch = lambda url, timeout=30, *, headers=None: next(responses).json()  # noqa: E731
    with pytest.raises(BugzillaProbeError) as excinfo:
        check_bugzilla("https://example.com", api_key="BAD", fetch=fetch)
    assert "invalid api key" in str(excinfo.value)


def test_check_bugzilla_accepts_valid_api_key():
    responses = iter([
        FakeResponse(200, {"version": "5.0.4"}),
        FakeResponse(200, {"id": 7, "name": "user@example.com"}),
    ])
    fetch = lambda url, timeout=30, *, headers=None: next(responses).json()  # noqa: E731
    assert check_bugzilla("https://example.com", api_key="GOOD", fetch=fetch) == "5.0.4"


def test_check_bugzilla_skips_whoami_without_key():
    calls = []

    def fetch(url, timeout=30, *, headers=None):
        calls.append(url)
        return {"version": "5.0.4"}

    assert check_bugzilla("https://example.com", fetch=fetch) == "5.0.4"
    assert calls == ["https://example.com/rest/version"]  # no whoami probe
