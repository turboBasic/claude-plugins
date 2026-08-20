---
name: write-issue
description: Author an issue or roadmap epic as product owner - one deliverable, evidence in the goal, acceptance boxes that can fail. Use when asked to open, draft or rewrite an issue or epic.
---

# Write an issue

**Acting as product owner.** It owns what the work is and for whom, never how it is built, and it does
not touch the tree the issue describes. An issue is written, never worked, and no record is written ahead
of the work — a decision the issue carries is named in it and ruled when the milestone holding it starts.

The repo's instruction layer owns what an issue and an epic each are, and how prose published to GitHub
is wrapped. Cite it rather than restating it.

## Before writing

**Look for the issue that already covers it.** Two issues on one deliverable both stay open and each
reads as the whole of the work. Where one exists, edit that body and comment what changed.

**Name the deliverable in one sentence about a person.** If that sentence will not come, this is not an
issue yet: it is a fragment of one, a decision, or a technical-debt entry.

## The body

1. **`## Goal` is the story, and it shows its evidence.** What is true now that should not be, with the
   `file:line`, the measured figure or the `gh` read that proves it. Not a task list — the tasks are the
   plan's.
2. **`## Done when` boxes are acceptance criteria that can fail.** "Consider whether X" cannot fail; "X
   exists, and a test pins it" can. Include the box that catches the regression, not only the boxes that
   describe the feature.
3. **A box already satisfied is not a box.** Check each against the tree first; where the answer is
   "already true", say so under a heading that is not `## Done when`.
4. **`## Decide in this issue` names a decision without settling it**, with each route and what it costs.
   Where a route would reverse something recorded or ruled, say which.
5. **Say what the issue is not**, where an adjacent thing would otherwise be assumed in — and name the
   issue or the register entry that holds it.
6. **Labels** come from the instruction layer's vocabulary, one of each axis it defines; absent one, one
   area, one `type:`, one `size:`. An epic carries the roadmap label alone.
7. **Wire the relationships**: the parent through `issues/<n>/sub_issues`, blocking through
   `issues/<n>/dependencies/blocked_by` — both by numeric id, per `groom-milestone` "GitHub mechanics".
   No `- Blocked by:` line in a body. `- Relates to:` stays prose. A section holding
   nothing else goes.
8. **Record what would otherwise be rediscovered** — a figure measured while writing, a defect verified
   in the tree, a route weighed and dropped. It goes in the body or a comment now, per `groom-milestone`
   "What earns a comment".

## An epic

A roadmap epic is the milestone's body, and it describes **what the milestone contains now**.

- The deliverable sentence, first, and the order between its threads if the order is the point.
- One paragraph per thread, naming the issue that owns it. Never a checklist of its children: the
  sub-issue panel is that, and the prose copy is the one that rots.
- **What left the milestone and why**, where anything did.
- **What the milestone must not do**, where a gate or an invariant bounds it.
- Where nothing numeric changes, say so — it is the sentence that tells a reader no answer can move.
