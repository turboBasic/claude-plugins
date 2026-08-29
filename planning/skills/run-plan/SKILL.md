---
name: run-plan
description: Execute one phase of a scratch implementation plan, each task verified, committed and ticked on its own. Use when asked to run, execute or continue a plan.
---

# Run a plan

**Acting as developer.** It owns executing a plan's tasks as written. It does not re-scope: a task this
role believes wrong goes back to the architect who wrote it.

The plan file is scratch — the commit and the issue checkbox are the durable half, so a ticked box is a
note to this session. `write-plan` owns what a plan file contains and where it lives; a plan's own ground
rules add to this loop without replacing it.

## Steps

1. **Locate the plan** in the directory `write-plan` names, matching the slug or description against what
   is there. More than one match: ask.
2. **Read the status line first.** A plan marked complete is frozen — say so and stop.
3. **Settle the scope before the first task, never during.** The default is the phase holding the first
   unchecked task, run to its end. Ask up front where the request reads narrower or wider — a scope
   question raised after the second commit is a question about work already landed.
4. **Read the plan's ground rules and the phase heading.** They constrain every task in the run. A
   `Model:` note the running session is weaker than stops the run before the first task; a stronger
   session is worth naming and no reason to stop.
5. **Execute the first unchecked task as written.** If executing it reveals the task is wrong, misordered
   or superseded, that ends the run: report it and ask. Do not rescope it and do not step over it.
6. **Verify** exactly what the `Verify:` line asks and nothing less. A `Verify:` naming a command means
   running it, not reasoning about what it would print.
7. **Run the gates the repo defines**, and fix what fails. `just --list` and `mise tasks` name them — a
   `ci` target, else `lint`, else the hook runner across all files. Stage new files first, since a hook
   runner reads tracked files only, so a run that passes over an untracked file has checked nothing.
   Re-stage what a hook reformats and re-run. A `Verify:` line may ask for less than every gate; it never
   licenses less.
8. **Land it, then tick the box, before the next task starts.** Settle which branch may receive a commit
   before the run's first one: the default branch, `git symbolic-ref refs/remotes/origin/HEAD`, is
   off-limits unless the instruction layer says otherwise, and a non-default branch is open unless the
   instruction layer names it. `gh api repos/:owner/:repo/rules/branches/<branch>` reports what is
   enforced, never what is permitted, and `branches/<branch>/protection`'s 404 is a ruleset it cannot see
   rather than an unprotected branch — neither answers the question. The task's change is one Conventional
   Commit, and the box is ticked once that commit exists — never before it, never batched to the phase
   boundary.
9. **Repeat from step 5 for the phase's remaining tasks**, then stop rather than rolling on.
10. **Review the phase's commits as the `review:architect` agent**, with the `review:change` skill
    where the repo enables it. The brief is a run-plan phase and the tasks it landed; `review:change`
    "What the brief may say, and what it may not" owns the rest of it. Once for the phase, not per task.
    A finding obliges one of three answers: a further commit inside this phase, a task appended to the
    next phase, or a debt entry per `write-plan` step 8. Ticked boxes stay ticked.
11. **Report** the tasks that landed, each finding and how it was answered, and what the next phase
    holds. A finding stays open, and with it the phase, until answered or the owner overrides it.

## Judgment

- **A failure ends the run only once it resists fixing.** A red gate is the work, not an exit. What ends
  the run is a failure this session cannot resolve — a missing credential, a task built on a decision
  nobody made, a gate demanding something outside the plan. Then the box stays unchecked and the report
  names the task and what failed.
- **An already-done task is verified and checked off, not redone.** Confirm the end state the task
  describes actually holds, then tick.
- **A task that names a non-negotiable is a stop, not a licence.**
