# tools

Each tool is a pair: `<tool>.yaml` (identity + description.llm + parameters) and
`<tool>.py` (`class <Tool>(Tool)` with `_invoke(...) -> Generator[ToolInvokeMessage]`;
add `from __future__ import annotations` so the single-arg `Generator[...]` annotation is
not evaluated at runtime under the 3.12 runner).
Register every tool in `provider/bugzilla.yaml` under `tools:`.
