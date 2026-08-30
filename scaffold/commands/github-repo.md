---
name: github-repo
description: Apply the GitHub repository baseline — merge methods, feature toggles, topics, security alerts and a protected default branch — to a repository, creating it first on request.
argument-hint: "<name|owner/name> [--create] [--public] [--description TEXT] [--homepage URL] [--topic T]... [--status-check CTX]... [--dry-run]"
model: sonnet
allowed-tools: Bash(python3:*)
---

# Apply the GitHub repository baseline

Assumes `gh` authenticated as the owner, and `python3` 3.7 or later on `PATH`.

1. Run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/repo_settings.py" $ARGUMENTS`. The script owns the
   baseline, the flags and the order of the calls: pass the invocation through unchanged, add
   nothing, and decide nothing it decides.

2. Read its output back — each `key: was -> will be` line, then whether it applied, was a dry run,
   or had nothing to change. Report a non-zero exit as it stands.

## Rules

- **`gh api` by hand is not the fallback.** A failed run is reported, not finished manually, and not
  retried under different flags.
- **A "no such file" failure means `${CLAUDE_PLUGIN_ROOT}` was not substituted** — report that.
