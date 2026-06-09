from bugzilla_client.http import api_key_headers
from bugzilla_client.search import format_search, quicksearch_url, search_bugs


def _fetch(payload, captured=None):
    def f(url, timeout=30, *, headers=None):
        if captured is not None:
            captured["url"] = url
            captured["headers"] = headers
        return payload
    return f


def test_quicksearch_url():
    url = quicksearch_url("https://example.com", "logrotate", limit=5)
    assert "quicksearch=logrotate" in url and "limit=5" in url and "include_fields=" in url


def test_quicksearch_url_has_no_api_key():
    url = quicksearch_url("https://example.com", "logrotate")
    assert "api_key" not in url


def test_search_bugs_returns_list(search_payload):
    bugs = search_bugs("https://example.com", "logrotate", fetch=_fetch(search_payload))
    assert bugs and "id" in bugs[0]


def test_search_api_key_sent_as_header(search_payload):
    captured: dict = {}
    search_bugs("https://example.com", "logrotate", api_key="SECRET",
                fetch=_fetch(search_payload, captured))
    assert "SECRET" not in captured["url"]
    assert captured["headers"] == api_key_headers("SECRET")


def test_format_search(search_payload):
    text = format_search(search_payload["bugs"], "logrotate")
    assert text.startswith("Found")
    assert "- " in text


def test_format_search_empty():
    assert "No bugs found" in format_search([], "zzz")
