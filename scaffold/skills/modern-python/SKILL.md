---
name: modern-python
description: The toolchain a modern Python project starts from - uv, hatchling, ruff, Pyright and the runtime libraries that go with them. Use when starting a Python project, when choosing its packaging, linting, typing, CLI, config, logging, HTTP or retry library, or when reading an existing project against the current stack.
---

# Modern Python toolchain

The stack a Python project starts from, and the one an existing project is read against. It states choices;
standing the project up is ordinary edits.

## The stack

| Concern | Tool |
| --- | --- |
| Packaging, dependencies, virtualenv | `uv` |
| Build backend | `hatchling` |
| Lint and format | `ruff` |
| Types | `Pyright`, strict |
| CLI parsing | `Typer` |
| Terminal output | `Rich` |
| Structured logging | `structlog` |
| Configuration | `Dynaconf` |
| Data at a boundary | `Pydantic v2` |
| HTTP | `httpx` |
| Retries | `tenacity` |
| AWS type stubs | `boto3-stubs` |
| CI | GitHub Actions |

## What the table does not say

- **One tool per concern.** `ruff` covers lint and format, so `black`, `isort`, `flake8` and `pylint` are one
  finding rather than four. `uv` covers dependencies and the virtualenv, so `pip`, `pip-tools` and
  `virtualenv` are too.
- **`Pyright` runs strict.** A narrowed setting is a decision to record wherever the repo records decisions,
  not a default to drift into.
- **`Pydantic` belongs at a boundary** — data arriving from a network, a file or a person — not on every
  internal structure.
- **`Dynaconf` is the only reader of the environment.** Configuration reaches the rest of the code as an
  argument, so nothing else reads it.
- **A tool absent from the table is absent on purpose.** Adding one is a choice to state, not to assume.

## A single-file script is not this

`uv run --script` with inline metadata is the whole answer: no packaging, no build backend, no layout.

## Where this yields

`.editorconfig` wins over anything here — indentation, line endings, charset, final newline. Read it before
writing.

Run the repo's own lint entry point over what changed rather than `ruff` directly, and resolve every finding
before reporting the work done.
