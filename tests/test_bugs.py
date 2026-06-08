from bugzilla_client.bugs import (
    bug_url,
    comments_url,
    fetch_bug,
    fetch_comments,
    format_bug,
    status_line,
)
from bugzilla_client.errors import BugNotFound


def _fetch(payload):
    def f(url, timeout=30):
        return payload
    return f


def test_bug_url_and_api_key():
    assert bug_url("https://example.com", "40000") == \
        "https://example.com/rest/bug/40000"
    assert "api_key=secret" in bug_url("https://example.com", "40000", api_key="secret")
    assert comments_url("https://example.com", "40000").endswith("/rest/bug/40000/comment")


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


def test_format_bug_compact(bug_payload, comments_payload):
    bug = bug_payload["bugs"][0]
    comments = comments_payload["bugs"]["40000"]["comments"]
    text = format_bug(bug, comments, "https://example.com")
    assert text.startswith("Bug 40000 [")
    assert "show_bug.cgi?id=40000" in text
    assert "Comments" in text
    assert "{" not in text  # compact text, not JSON
