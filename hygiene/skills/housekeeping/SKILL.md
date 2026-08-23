---
name: housekeeping
description: Audit repository hygiene as architect - the gates, instruction-layer duplication, stale permission rules and whatever else the repo declares - and report the findings without fixing them. Use when asked for a repo audit, a hygiene check or a housekeeping pass.
---

# Housekeeping sweep

**Acting as architect.** It owns what counts as drift across the repository. It does not implement, not
even the one-line fix a finding makes obvious.

Run every check even when an earlier one fails: a broken gate says nothing about the rest.

## Checks

1. **Gates.** Run the repo's own gate, which `just --list` and `mise tasks` name. Each failure is a
   finding,
   quoted with the file and line the tool printed. A hook that rewrites a file is a finding too — the
   rewrite is drift that was sitting in the tree, even though the hook repaired it.
2. **Duplication.** `hygiene:update-docs` owns the one-owner rule and the test for a repeat; this check
   applies them wider than the docs, across the live Markdown of the instruction layer, `.claude/skills/`,
   `.claude/agents/`, the pointer files under `.github/`, and the human-facing layer. Report, never edit.
3. **Stale permissions.** Every `.claude/settings*.json` in the repo names permission rules by path and
   command name; the user-level file is out of scope. A rule naming a task, skill, script or file that no
   longer exists is a finding. Glob patterns covering a directory are not — they age fine.
4. **What the repo declares its own.** The instruction layer names any further check this sweep owes it —
   a structure tree against the filesystem, a debt register against its conditions, a sync state against
   its staleness window. Run each as written there and report it beside the rest.

## Reporting

Group findings by check, most consequential first, and say plainly when a check is clean. Where a fix is
one command, name the command. Where it is a judgment — a duplicated fact needing a home, a debt entry now
due — state what you would do and why, and leave it to the user.
