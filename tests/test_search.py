from bugzilla_client.search import format_search, quicksearch_url, search_bugs


def _fetch(payload):
    def f(url, timeout=30):
        return payload
    return f


def test_quicksearch_url():
    url = quicksearch_url("https://example.com", "logrotate", limit=5)
    assert "quicksearch=logrotate" in url and "limit=5" in url and "include_fields=" in url


def test_search_bugs_returns_list(search_payload):
    bugs = search_bugs("https://example.com", "logrotate", fetch=_fetch(search_payload))
    assert bugs and "id" in bugs[0]


def test_format_search(search_payload):
    text = format_search(search_payload["bugs"], "logrotate")
    assert text.startswith("Found")
    assert "- " in text


def test_format_search_empty():
    assert "No bugs found" in format_search([], "zzz")
