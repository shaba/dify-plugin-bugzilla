# tools

Each tool is a pair: `<tool>.yaml` (identity + description.llm + parameters) and
`<tool>.py` (`class <Tool>(Tool)` with `_invoke(...) -> Generator[ToolInvokeMessage]`).
Register every tool in `provider/bugzilla.yaml` under `tools:`.
