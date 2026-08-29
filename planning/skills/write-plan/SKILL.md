---
name: write-plan
description: Author a scratch implementation plan whose tasks are one green commit each, ending in a Verify line that can fail. Use when asked to write or decompose an implementation plan.
---

# Write a plan

**Acting as architect.** It owns the plan, never the tree the plan is written against.

A plan is `tmp/plans/<slug>.plan.md`, scratch and never committed — add `tmp/` to `.gitignore` where it is
missing. The shape is this skill's, read off nothing: no frontmatter, with a **Status line** directly
under the title reading `**Status: in progress (YYYY-MM-DD).**` or `**Status: complete (YYYY-MM-DD).**`;
**Ground rules**; **Out of scope**; **Phases** grouping tasks, optionally carrying a `Model:` note;
**Tasks** as checkboxes numbered `<phase>.<task>`, each ending in a `Verify:` line; and **Technical
debt** holding identifiers only.

`run-plan` executes the result literally — first unchecked task, top to bottom, as written, gated,
committed.

## Steps

1. **Start from the issue, not a blank plan.** Read the whole thread and the epic above it. Where the
   plan must depart from the issue, the departure is a comment on the issue before it is a task here.
2. **Measure the tree before drafting.** Read the files the work will touch, run the gates, cite line
   numbers, measured figures and what a command printed. A task naming what it will change is
   executable; a task naming a goal is a wish.
3. **Decompose into tasks first, write the sections after.** Order them so each is executable when
   reached — a task needing a later one is a stall the executor cannot resolve.
4. **Size every task to one commit that leaves the tree green.** `run-plan` gates and commits after each
   task, so a task that only compiles once its successor lands can never pass. The shape that works is
   usually declare, then wire, then fill.
5. **Write each `Verify:` so that it can fail.** Name a command and what its output must show, or a
   state a reader can check and disagree with — "tests pass" verifies nothing, since the gates run
   anyway. Prefer the assertion that would have caught the mistake you are worried about, and one the
   work cannot satisfy by editing itself: "the tolerance assertion passes" is met by widening the
   tolerance, "the same 1 test runs before and after" is not. A task that resists a checkable
   verification is not yet understood — split it until one is available.
6. **Phase only where the grouping carries information** — a shared prerequisite, a change of subject, a
   `Model:` the phase expects. A boundary is where the plan is handed back for a look, so put it where a
   look is worth taking.
7. **Make every Ground rule and Out of scope entry rule something out.** A ground rule names a mistake
   available in *this* work, not a convention the instruction layer already binds. An Out of scope entry
   carries the reason it lost.
8. **Make the last task land what outlives the file.** The issue's checkboxes and the epic's box
   ticked — not closed, the PR's `Closes #N` does that — the status line set to complete with the
   date, and every remaining obligation given a home: an issue where it is work someone will do, or
   the technical-debt register, the one `rg --files -g '*technical-debt*'` finds, where it states a
   condition the repository can answer. Where no register exists, or the entry would state no
   condition a sweep can evaluate, say so and ask. The Technical debt section names the identifiers
   of whatever entries exist, and says so when there are none.

## Judgment

- **A task is phrased as an end state, not an action** — "add the module" is ambiguous the moment the
  module exists.
- **A report-only task must land something durable** — a register entry, a term in a list, a
  corrected document.
- **A task that would break a non-negotiable does not belong in a plan.** A plan is not authorisation.
- **Tasks coming out as "decide X" mean the decision is not made.** Those belong in the issue thread or
  a record.
