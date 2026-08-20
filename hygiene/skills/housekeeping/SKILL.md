---
name: housekeeping
description: Audit repository hygiene as architect - the gates, instruction-layer duplication, the technical-debt register, the stale local allowlist and whatever else the repo declares - and report the findings without fixing them. Use when asked for a repo audit, a hygiene check or a housekeeping pass.
---

# Housekeeping sweep

**Acting as architect.** It owns what counts as drift across the repository. It does not implement, not
even the one-line fix a finding makes obvious.

Report-only. Run every check, then hand the user one list; a sweep that fixes as it goes buries what drifted
under the repair. Each finding names what drifted, the file that owns it, and the fix — the user decides
which fixes happen, and each one is separate work afterwards.

Run every check even when an earlier one fails: a broken gate says nothing about the rest.

## Checks

1. **Gates.** Run the repo's own gate, named by its instruction layer; absent a rule, the task runner's
   `ci` target, else its `lint` target, else the hook runner across all files. Each failure is a finding,
   quoted with the file and line the tool printed. A hook that rewrites a file is a finding too — the
   rewrite is drift that was sitting in the tree, even though the hook repaired it.
2. **Duplication.** Every fact has one owner; a mention anywhere else is a citation of that owner or a
   finding. Read the live Markdown — the instruction layer, `.claude/skills/`, `.claude/agents/`, the
   pointer files under `.github/`, and the human-facing layer — and apply the route-or-fact test: delete
   the sentence mentally and ask whether a route or a fact was lost. Reading is the check; a term list
   would only find drift someone already noticed.

   The enforcement details are where it bites, because prose naming one has copied a fact a config file
   owns and will not be corrected when that file changes: a lint level, a task's command line, a hook's
   name, a pinned version, a threshold. Restatement is sanctioned in three places and not worth listing —
   an invariant list in the instruction layer, a decision record that decided a fact, and the human-facing
   layer, which restates by licence. A human-layer hit is a finding only when it contradicts its owner or
   pins an enforcement detail.
3. **Technical-debt register.** `docs/technical-debt.md` holds every entry the repository has recorded. Take
   the live ones, answer each condition against the repository rather than from memory, and report the ones
   now true. An entry whose condition has not fired is not a finding and is not worth listing; a deferred
   one whose condition the repository *cannot* answer is, because it will read as deferred forever. Skip the
   entries whose labels record that they are closed — a retired entry's condition is unanswerable by
   construction, which is the whole of what retiring it recorded. **A missing register is itself a
   finding**, since the checks below cannot tell an empty one from an absent one.
4. **Stale local allowlist.** `.claude/settings.local.json`, if it exists, grants permissions by path and
   command name. An entry naming a task, skill, script or file that no longer exists is a finding. Glob
   patterns covering a directory are not — they age fine.
5. **What the repo declares its own.** The instruction layer names any further check this sweep owes it —
   a structure tree against the filesystem, a data registry against its rows, a sync state against its
   staleness window, a record set against its ceiling and its label vocabulary. Run each as written there
   and report it beside the four above. A repo naming none is complete at four.

## Reporting

Group findings by check, most consequential first, and say plainly when a check is clean. Where a fix is
one command, name the command. Where it is a judgment — a duplicated fact needing a home, a debt entry now
due — state what you would do and why, and leave it to the user.

A sweep that finds nothing is a useful result. Report it as such rather than promoting a near-miss to fill
the list.
