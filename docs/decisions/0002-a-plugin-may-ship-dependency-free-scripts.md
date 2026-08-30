---
id: 0002
status: accepted
date: 2026-08-30
scope: marketplace
---

# ADR 0002 — A plugin may ship dependency-free scripts, and that is not a project

## Decision

A plugin authored here may ship executable code under `<plugin>/scripts/`, importing only its
language's standard library, in Python and no second language. It brings no packaging of its own: no
`pyproject.toml`, no lockfile, no lint or type configuration inside the plugin directory. Its checks
are hooks in the existing `.pre-commit-config.yaml`, selected by a `mise` task like every other gate,
and the behavioural check it carries is a `--self-check` flag over its own pure functions.

## Context

`scaffold` needs to apply a GitHub repository baseline — merge methods, wiki and discussions off,
topics, security alerts, a branch ruleset. Every payload must be identical on every run, so that a
second run over the same repository changes nothing. Prose cannot promise that: a model re-deriving
those payloads from a description is the drift the baseline exists to remove.

The instruction layer had ruled the opposite by anticipation — the gate "runs nothing a plugin
ships", and the first plugin needing to run "brings its whole project inside the plugin directory".
That was written with no such plugin in hand; standing one up measured the cost, which the `uv`
option below carries. `gh` absorbs what a dependency otherwise would: authentication across three
accounts, hosts, retries and pagination stay its problem, which is what keeps the dependency list
empty rather than merely short.

## Options

### One stdlib script, checks at the repository root (SELECTED)

- Adopted because: determinism is the whole point, and it costs one file.
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
- Rejected despite: one file still, and no packaging.

### A `bash` script with `gh api --jq`

- Rejected because: `ruleset_shape`'s nested projection is worse in `jq`, and it guards idempotence.
- Rejected despite: it avoids this record's whole cost — no interpreter, no ruff, no debt row.

### Leave it prose and let the model make the calls

- Rejected because: the failure is silent — a dropped field reads as "no change" in the report.
- Rejected despite: no new file type, no gate change, no record needed.

## Consequences

`mise run ci` now executes something this repository ships, so the gate is no longer a pure reader,
and Python becomes a file type this repository registers. `plugin-version-bumped` widens to
`<p>/scripts`, without which a script-only edit ships against the copy a consumer already installed.
The evidence is a run: this repository took the baseline on 2026-08-30, dropping `has_wiki` and
`allow_merge_commit` and gaining `protect-default-branch`, and a second run reported nothing to change.

Types are unchecked. [TD-01](../technical-debt.md) holds it, and owns the condition it comes due on.

Reopen on a third-party import, a second language, or a script grown past what one `--self-check`
can hold — never on a file count, which the gate cannot see: splitting one script in two costs
nothing, while the first script in a second plugin costs a hook.

## Links

- [PR #23](https://github.com/turboBasic/claude-plugins/pull/23) — the script, the command, the gate.
