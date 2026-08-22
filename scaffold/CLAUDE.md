# scaffold — how the milestone runner works

Design notes for maintaining this plugin. The root `CLAUDE.md` and `docs/ai-instructions.md` govern the
repository; this file covers only the runner, and is why the plugin's code is legible without reading it
all.

Claude Code plugin that scaffolds modern Python projects via a milestone loop.

## Architecture

The plugin drives a `claude` subprocess once per milestone. The runner is
the source of truth — it verifies completion, tracks state, and retries. The agent never
self-reports success.

```text
src/milestone_runner/
  cli.py         ← Typer entry point; parses args, creates EventLog, calls runner.run()
  runner.py      ← main loop: iterates milestones, orchestrates attempts
  agent.py       ← builds prompt, invokes claude --print, parses agent JSON output
  verify.py      ← runs verify.sh, parses structured result
  context.py     ← RunContext Pydantic model; create/load/save agent.context.json
  escalation.py  ← model ladder: haiku → sonnet → opus per attempt
  interaction.py ← TTY prompts on loop exhaustion (skip / retry with hint / abort)
  events.py      ← typed JSONL event log
  state.py       ← .milestones-completed and milestones-summary.json
  summary.py     ← human-readable log reader (also exposed as scripts/log_summary.py)
  models.py      ← shared Pydantic types (AgentResult, VerifyResult, CheckResult)

milestones/
  01-scaffold/
    milestone.toml ← milestone properties
    PROMPT.md      ← prompt for LLM code generation
    generate.py    ← script for deterministic code generation
    verify.sh      ← pass/fail checks run by the runner, never by the agent
  02-pre-commit/
  03-ci/
  04-config/
  05-http/
  06-aws/        ← conditional on --aws
  07-tests/
    PROMPT.md    ← steps the agent executes
    verify.sh    ← pass/fail checks run by the runner, never by the agent

scripts/
  log_summary.py      ← thin wrapper; calls milestone_runner.summary
  validate_pyproject.py ← standalone validator called from verify.sh

commands/
  new-python-project.md ← slash command entry point
```

## Milestones

| #   | Name       | Conditional?          |
| --- | ---------- | --------------------- |
| 01  | scaffold   | no                    |
| 02  | pre-commit | no                    |
| 03  | ci         | no                    |
| 04  | config     | no                    |
| 05  | http       | no                    |
| 06  | aws        | yes — only if `--aws` |
| 07  | tests      | no                    |

Milestone ordering reflects the dependency graph: CI (03) has no dependency on config/http/aws
so it runs early. Tests (07) run last because they depend on everything else existing.

## Verify scripts

Each `verify.sh` emits a JSON result to stdout and exits 0 only when all checks pass:

```json
{"milestone": "01-scaffold", "passed": true, "checks": [
  {"name": "pyproject.toml exists", "ok": true},
  {"name": "uv.lock exists", "ok": false, "detail": "run: uv sync --all-groups"}
]}
```

`verify.py` parses this; `fails` is derived from `checks[*][ok=false].name`.
Scripts that predate the JSON contract fall back to `FAIL:` line parsing.

`07-tests/verify.sh` also runs `mise exec -- just --quiet test` after structural checks,
gated on all checks passing to avoid running a broken test suite.

## State files (in the generated project root)

| File                     | Owner            | Purpose                                                      |
| ------------------------ | ---------------- | ------------------------------------------------------------ |
| `agent.context.json`     | `cli.py` (once)  | project metadata for every agent invocation; never modified  |
| `.milestones-completed`  | `state.py`       | one short name per line; written after `verify.sh` exits 0  |
| `milestones-summary.json`| `state.py`       | per-milestone notes accumulated across milestones            |
| `agent-<ts>.log.jsonl`   | `events.py`      | all invocation-level events                                  |
| `agent-latest.log.jsonl` | `cli.py`         | symlink → most recent log                                    |

`agent.context.json` keys: `project_name`, `package_name`, `description`, `project_dir`,
`plugin_dir`, `flags`, `milestones`. Never modified by the agent.

`flags` carries `["--aws"]` when `--aws` was set; empty list otherwise.

## Retry logic

`runner.py` retries each milestone up to 3 total attempts (2 retries). On retry, FAIL lines
from `verify.sh` output are prepended to the prompt so the agent knows what to fix. After 3
failed attempts the runner calls `interaction.py` to prompt the user (skip / retry with hint /
abort) unless `--non-interactive` is set, in which case it exits non-zero immediately.

The agent does **not** run `verify.sh` — that is the runner's job. The agent ends its
response with a JSON result object: `{"status": "done", "milestone": "...", "notes": [...]}`.

## Log events

```text
run_started               project, milestones
milestone_started         milestone, attempt, model
agent_output              output (raw agent response)
verify_result             milestone, exit_code, result (parsed JSON)
milestone_completed       milestone, attempt, notes
milestone_failed          milestone, attempt, fails
milestone_skipped         milestone[, reason]
milestone_timeout         timeout
run_completed             project
run_aborted               milestone
```

## CLI flags

| Flag                | Default    | Purpose                                                         |
| ------------------- | ---------- | --------------------------------------------------------------- |
| `project_name`      | (required) | name of the project to generate                                 |
| `description`       | `""`       | one-line description embedded in context                        |
| `--aws`             | off        | include the 06-aws milestone                                    |
| `--output-dir`      | `.`        | parent directory for the generated project                      |
| `--context PATH`    | —          | resume from existing `agent.context.json`; skips all other args |
| `--timeout SECONDS` | `300`      | per-milestone agent subprocess timeout                          |
| `--non-interactive` | off        | abort on loop exhaustion without prompting (auto-set on non-TTY)|

Running without `--context` against a project that already has `agent.context.json` is an
error — the runner fails fast and prints the correct `--context` invocation.

## Invocation

```bash
# first run
mise exec -- uv run --project <plugin_dir> milestone-runner run <project-name> "<description>" [--aws] [--output-dir DIR]

# resume
mise exec -- uv run --project <plugin_dir> milestone-runner resume <project_dir>/agent.context.json

# read log
mise exec -- uv run --project <plugin_dir> milestone-runner log-summary [log_file]
# default: agent-latest.log.jsonl in cwd
```

## Design decisions

- **Runner owns verification.** Agents under `--print` do the main task reliably but skip
  side-effects like bookkeeping. The runner calls `verify.sh` independently.

- **Agent is sandboxed to `project_dir`.** The agent must not read, inspect, or modify any
  file outside `project_dir`. This prevents monorepo config (e.g. `uv` workspace) from leaking
  into generated projects. Every file path operation must resolve within `project_dir`.

- **`agent.context.json` is immutable after creation.** The agent reads it but never writes it.
  Re-runs must use `--context` — no silent flag override is possible.

- **Loop A removed.** The agent originally ran `verify.sh` itself (loop A) before the runner
  ran it (loop B). After H1 added `just test` to `07-tests/verify.sh`, this caused two full
  test suite runs per attempt. Loop A was removed; the runner's loop B is sufficient.

- **`claude --print` does not auto-load CLAUDE.md.** Any instructions in CLAUDE.md are
  invisible to agent subprocesses unless explicitly injected into the prompt. See I27.

## Code style

- Class docstrings are allowed and encouraged for public classes. Prefer short one-line
  docstrings.

## Code patterns (apply to all milestones)

- Config injection: `AppConfig` is always passed as a function argument. Never import
  from bootstrap or read environment variables directly inside a module.
- Dynaconf boundary: only `bootstrap.py` imports dynaconf. All other code depends on `AppConfig`.
- Logging: use `structlog` everywhere. Call `configure_logging()` only from `cli.py`.
- Async bridge: Typer commands are synchronous. Use `asyncio.run()` to call async functions.
- Dependencies: add to `pyproject.toml` via `uv add`, never edit the file manually for deps.
- Tooling: all tool invocations go through `mise exec -- <tool>`.
