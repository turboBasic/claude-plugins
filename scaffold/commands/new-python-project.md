---
description: Scaffold a modern Python project
argument-hint: "run <project-name> [description] [--aws]"
---

# new-python-project

Run the wrapper script that drives the `modern-python` agent milestone by milestone.

```bash
mise exec -- uv run --project "$CLAUDE_PLUGIN_DIR" milestone-runner $ARGUMENTS
```

## Substrate

**This command runs code shipped inside the plugin, and nothing in the manifest declares what that
needs.** It assumes:

- **`uv`**, and **`mise`** to reach it. Without `uv` the line above fails in the shell rather than
  reporting anything useful — check `command -v uv` first and say that is what is missing.
- **Python 3.14 or newer**, which `scaffold/pyproject.toml` requires. `uv` fetches it if the version is
  absent, so a first run may be slow rather than broken.
- **Network access on that first run**, to resolve the locked dependencies.

The runner then invokes `claude` itself per milestone, so it needs this CLI on `PATH` too.

**None of this is checked for you.** Where a prerequisite is missing, name the missing one and stop —
do not fall back to scaffolding the project by hand, because the milestone verification is the point
and hand-scaffolding skips it.
