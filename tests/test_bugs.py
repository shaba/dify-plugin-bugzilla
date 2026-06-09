from bugzilla_client.bugs import (
    bug_url,
    comments_url,
    fetch_bug,
    fetch_comments,
    format_bug,
    status_line,
)
from bugzilla_client.errors import BugNotFound, BugzillaAuthError
from bugzilla_client.http import api_key_headers


def _fetch(payload, captured=None):
    def f(url, timeout=30, *, headers=None):
        if captured is not None:
            captured["url"] = url
            captured["headers"] = headers
        return payload
    return f


def test_bug_urls_never_carry_secret():
    # The api_key must travel in a header, never the URL.
    assert bug_url("https://example.com", "40000") == \
        "https://example.com/rest/bug/40000"
    assert comments_url("https://example.com", "40000").endswith("/rest/bug/40000/comment")
    assert "api_key" not in bug_url("https://example.com", "40000")


def test_api_key_sent_as_header_not_url(bug_payload):
    captured: dict = {}
    fetch_bug("https://example.com", "40000", api_key="SECRET",
              fetch=_fetch(bug_payload, captured))
    assert "SECRET" not in captured["url"]
    assert captured["headers"] == api_key_headers("SECRET")
    assert captured["headers"]["X-BUGZILLA-API-KEY"] == "SECRET"


def test_fetch_bug_returns_first(bug_payload):
    bug = fetch_bug("https://example.com", "40000", fetch=_fetch(bug_payload))
    assert bug["id"] == 40000
    assert bug["summary"]


def test_fetch_bug_not_found():
    for payload in ({"bugs": []}, {"error": True, "message": "not found"}):
        try:
            fetch_bug("https://example.com", "1", fetch=_fetch(payload))
        except BugNotFound:
            continue
        raise AssertionError("expected BugNotFound")


def test_status_line():
    assert status_line({"status": "CLOSED", "resolution": "FIXED"}) == "CLOSED FIXED"
    assert status_line({"status": "NEW", "resolution": ""}) == "NEW"


def test_fetch_comments(comments_payload):
    comments = fetch_comments("https://example.com", "40000", fetch=_fetch(comments_payload))
    assert comments and "text" in comments[0]


def test_fetch_comments_error_raises_auth():
    # A permission rejection on the comment endpoint is an auth error, not 'not found',
    # so the bug_get tool can still render the bug it already fetched.
    payload = {"error": True, "message": "You are not authorized"}
    try:
        fetch_comments("https://example.com", "40000", fetch=_fetch(payload))
    except BugzillaAuthError:
        return
    raise AssertionError("expected BugzillaAuthError for an error response")


def test_fetch_comments_fallback_single_entry():
    # User passes a non-canonical id form; map is keyed by the canonical id but has one
    # entry, so the comments should still be resolved.
    payload = {"bugs": {"40000": {"comments": [{"text": "hi", "count": 0}]}}}
    comments = fetch_comments("https://example.com", "040000", fetch=_fetch(payload))
    assert comments and comments[0]["text"] == "hi"


def test_format_bug_handles_missing_count():
    bug = {"id": 1, "status": "NEW", "summary": "x"}
    comments = [{"creator": "a@b", "creation_time": "2021-01-01", "text": "hi"}]
    text = format_bug(bug, comments, "https://example.com")
    assert "#None" not in text


def test_format_bug_compact(bug_payload, comments_payload):
    bug = bug_payload["bugs"][0]
    comments = comments_payload["bugs"]["40000"]["comments"]
    text = format_bug(bug, comments, "https://example.com")
    assert text.startswith("Bug 40000 [")
    assert "show_bug.cgi?id=40000" in text
    assert "Comments" in text
    assert "{" not in text  # compact text, not JSON
