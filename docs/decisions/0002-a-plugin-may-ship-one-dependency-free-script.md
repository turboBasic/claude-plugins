---
id: 0002
status: accepted
date: 2026-08-30
scope: marketplace
---

# ADR 0002 — A plugin may ship one dependency-free script, and that is not a project

## Decision

A plugin authored here may ship executable code as a single script under `<plugin>/scripts/`,
importing only its language's standard library. It brings no packaging of its own: no
`pyproject.toml`, no lockfile, no lint or type configuration inside the plugin directory. Its checks
are hooks in the existing `.pre-commit-config.yaml`, selected by a `mise` task like every other gate,
and the behavioural check it carries is a `--self-check` flag over its own pure functions. A second
script in one plugin, or any third-party import, exhausts this and reopens the question.

## Context

`scaffold` needs to apply a GitHub repository baseline — merge methods, wiki and discussions off,
topics, security alerts, a branch ruleset. Nine API calls whose payloads must be identical every run,
so that a second run over the same repository changes nothing. Prose cannot promise that: a model
re-deriving nine payloads from a description is the drift the baseline exists to remove.

The instruction layer had ruled the opposite by anticipation — the gate "runs nothing a plugin
ships", and the first plugin needing to run "brings its whole project inside the plugin directory".
That was written with no such plugin in hand. Standing one up measured the cost: `uv` in the gate, a
second lockfile to renew, a nested lint configuration, and `uv sync` in every consumer's clone — all
to serve one file importing `argparse`, `json`, `subprocess` and `sys`. `gh` absorbs the rest:
authentication across three accounts, hosts, retries and pagination stay its problem, which is what
keeps the dependency list empty rather than merely short.

## Options

### One stdlib script, checks at the repository root (SELECTED)

- Adopted because: determinism is the whole point, and it costs one file plus three hook ids.
- Adopted because: nothing a consumer installs changes — no sync step, no lockfile, no virtualenv.
- Adopted despite: no typecheck, recorded as debt rather than solved.
- Adopted despite: `subprocess` to a CLI is a coarser boundary than a typed HTTP client.

### A `uv` project inside the plugin directory

- Rejected because: a second lockfile and lint configuration to keep from drifting, for one file.
- Rejected because: it puts `uv sync` between a consumer and a command that needs nothing else.
- Rejected despite: this is what the instruction layer anticipated, and what `modern-python` says.

### A PEP 723 script with inline `dependencies`

- Rejected because: `httpx` buys nothing `gh api` does not, and re-implements token handling across
  three authenticated accounts.
- Rejected because: it makes `uv` a runtime requirement of the command, not just of this repository.
- Rejected despite: one file still, and `modern-python` already names this shape for a lone script.

### Leave it prose and let the model make the calls

- Rejected because: nine payloads re-derived per run is the drift being removed, and the failure is
  silent — a dropped field reads as "no change" in the report.
- Rejected despite: no new file type, no gate change, no record needed.

## Consequences

`mise run ci` now executes something this repository ships, so the gate is no longer a pure reader:
`.pre-commit-config.yaml` grows `ruff-check`, `ruff-format` and a local `repo-settings-self-check`
hook, reached by `mise run lint:python`. `plugin-version-bumped` widens to `<p>/scripts`, without
which a script-only edit ships against the copy a consumer already installed. Python becomes a file
type this repository registers: `.editorconfig` gains `[*.py]`, `.gitignore` gains `__pycache__/` and
`.ruff_cache/`, and `cspell` gains the `python` dictionary.

Types are unchecked. TD-01 holds it, due when a second Python file joins `scaffold/scripts/` — the
point at which a nested project stops being overhead and this ruling is reopened anyway.

Reopen if a plugin here needs a second script, a third-party import, or a language whose standard
library cannot reach an authenticated HTTP API through a CLI already on the box.

## Links

- [PR #23](https://github.com/turboBasic/claude-plugins/pull/23) — the script, the command, the gate.
