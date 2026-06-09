# dify-plugin-bugzilla

A Dify tool plugin that reads from any Bugzilla instance (read-only): fetch a bug by id
and search bugs by a free-text query. The target Bugzilla is configured per credential
via `base_url`, so a single installation works with any Bugzilla server.

## Configuration

- `base_url` (required) — base URL of the Bugzilla instance, e.g. `https://example.com`
  (the REST API is served under `/rest`).
- `api_key` (optional) — Bugzilla API key, needed only to access non-public bugs.

## Tools

### `bug_get`

Fetch a bug by id (`/rest/bug/{id}` and `/rest/bug/{id}/comment`): status and resolution,
product and component, severity, the first comments, and a link.

- `bug_id` (string, required) — numeric bug id.

### `bug_search`

Search bugs via Bugzilla quicksearch (`/rest/bug?quicksearch=...`): id, status, summary,
product and component.

- `query` (string, required) — quicksearch query.
- `limit` (number, optional, default 15, range 1–50) — maximum number of results to return.

## Development

```sh
python3 -m pytest -q
ruff check .
yamllint .
```

The Bugzilla logic (REST client, bug fetch, search, formatting) lives in the
`bugzilla_client` package, which is independent of the Dify SDK and covered by unit tests
with mocked network calls. The tool and provider classes are thin adapters over it.

Bugzilla REST API reference: <https://bmo.readthedocs.io/en/latest/api/index.html>

## License

Apache-2.0. Copyright © 2026 Alexey Shabalin.

## Repository

<https://github.com/shaba/dify-plugin-bugzilla> — issues and pull requests welcome.
