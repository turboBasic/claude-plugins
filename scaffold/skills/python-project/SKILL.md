---
name: python-project
description: Point at the milestone-driven generator for standing up a new Python project. Use when asked to start, scaffold or bootstrap a Python project, service or CLI from nothing, or for a pyproject with linting, CI, config, HTTP or AWS layers already wired.
---

# Standing up a new Python project

**Hand the invocation over; do not scaffold by hand.** `scaffold` generates a project one milestone at a
time — pyproject, pre-commit, CI, config, HTTP, AWS, tests — and each milestone has its own check that
must pass before the next starts. Writing the files directly produces something that looks similar and
was never verified, which is the one outcome this plugin exists to prevent.

So the answer to "set up a Python project" is the command, run by the human:

```text
/scaffold:new-python-project run <project-name> [description] [--aws]
```

`--aws` adds the AWS service layer. `/scaffold:new-python-project` on its own reports the argument list.

**That command owns the rest** — the exact invocation, the toolchain it assumes, and what to do when a
prerequisite is missing. Read it rather than restating it here.

## When this is the wrong tool

- **An existing project.** The generator starts from nothing; it does not retrofit. Individual concerns —
  a pre-commit config, a CI workflow — are ordinary edits.
- **A one-file script.** `uv run --script` with inline metadata is the whole answer.
- **Another language.** Nothing here scaffolds Go, Rust or Node; say so rather than improvising a
  milestone set.
