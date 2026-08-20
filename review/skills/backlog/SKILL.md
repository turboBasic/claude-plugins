---
name: backlog
description: Read a milestone as product owner and produce the reading - the deliverable as one sentence about a person, and a keep, cut, split or resize answer per issue. Changes nothing. Use when asked whether the backlog is the right shape.
---

# Read a backlog

**Acting as product owner** ([`product-owner`](../../agents/product-owner.md)). The limit this workflow
adds: it changes **nothing at all** — not an issue, not a label, not an edge. The deliverable is the
reading; executing it is `planning:groom-milestone`'s. A reading that has already moved an issue took the
decision it was asked to inform.

Read the milestone's epic before its children. An epic describing what the milestone used to contain is the
finding that explains most of the others.

## The reading

1. **State the milestone's deliverable as one sentence about a person**: who can do what afterwards that
   they cannot do now. Where the title describes only some of its issues, that mismatch is the finding — a
   milestone carrying two themes has two customers and no legible deliverable.
2. **Derive the work from what that person's walk consumes.** Write the walk as the commands they run, then
   ask of each step what it actually reads. A field nothing in the walk consumes belongs to a later
   milestone even when an issue in this one lists it.
3. **Sort every acceptance box into one of four kinds**, checked against the tree rather than recalled: a
   one-time data or document edit; code someone runs; machinery whose only job is holding two copies in
   agreement; or already satisfied by something committed. The last two are where a milestone shrinks, and
   machinery to hold copies in step is nearly always avoidable by deleting one of the copies.
4. **Verify before believing a box.** Measure the figure, read the config, run the gate. A box asserting
   that some check exists is wrong often enough to be worth checking every time.
5. **Answer for each issue**, with a reason:
   - **Keep** — it has a deliverable of its own.
   - **Cut** — its consumers all live in a later milestone, or its only visible surface exists to
     demonstrate an internal component. Name where each part of it should go; no scope is lost if that is
     stated.
   - **Split or merge** — it holds two deliverables, or half of one.
   - **Resize** — the band it carries is wrong against what it now contains.

Weigh each answer against the smallest thing that serves the person in step 1, not against the issue it
replaces. An issue that shrinks to a paragraph, or to nothing, is this workflow working.
