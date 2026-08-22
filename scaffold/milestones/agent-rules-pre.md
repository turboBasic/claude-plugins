<!-- pyml disable MD041 -->

<!-- These rules are inserted before every PROMPT.md -->

## Global Rules

- **Scope**: do not modify files outside of `project_dir`.
- **Paths**: all paths are relative to `project_dir`. All commands run from `project_dir`.
- **Global context**: read `agent.context.json` for project metadata. Use only the keys listed in the "Context keys" line at the top of the milestone.
- **Tooling**: all tool invocations go through `mise exec -- <tool>`.
- **Dependencies**: add to `pyproject.toml` via `uv add`, never edit the file manually for deps.
- **Output format**: your very last line of output must be a single JSON object on one line matching this exact schema — no other text, no markdown fence, no blank lines after it:

  `{"status": "done", "milestone": "<milestone-name>", "notes": ["<string>", ...]}`

  - `status`: always the literal string `"done"`.
  - `milestone`: the short name (e.g. `"scaffold"`, `"http"`).
  - `notes`: a JSON array of strings. Each string is one decision or fact from the `## Notes` section of this milestone. Minimum 1 entry, no empty strings, no nested objects.
  - Do not emit this object more than once. Do not wrap it in a code fence. Do not place any text after it.

## Global Python code composition rules

- **Config injection**: `AppConfig` is always passed as a function argument. Never import from bootstrap or read environment variables directly inside a module.
- **Dynaconf boundary**: only `bootstrap.py` imports dynaconf. All other code depends on `AppConfig`.
- **Logging**: use `structlog` everywhere. Call `configure_logging()` only from `cli.py`.
- **Async bridge**: Typer commands are synchronous. Use `asyncio.run()` to call async functions.
