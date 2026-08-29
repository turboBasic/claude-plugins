---
name: review-change
description: Review a landed change as architect - what in the diff decided whether it passed, then the diff against the four concerns. Use when a plan's phase has landed, or when asked for an architecture review of a diff or branch.
---

# Review a change

**Acting as architect** ([`architect`](../../agents/architect.md)). The limit this workflow adds: the
deliverable is the verdict, and a finding is answered by whoever holds the tree — in a further commit, a
task on the next phase, or an entry in the technical-debt register `write-plan` names.

## What is already settled

**A gate is not re-run**, so what follows is how to know what the gates covered without running anything.

- **A commit implies its hooks ran** on the files it matches — the formatters, the linters, the spell
  check, the message check. The repo's pre-commit config is the roster.
- **A commit implies nothing about typecheck or tests**, which no hook runs. Those are the two facts a
  caller has to state.
- **A phase run by `run-plan` implies both**, because it runs the full gates before every commit in the
  range.
- **A pushed ref needs no claim at all.** `gh api repos/:owner/:repo/commits/<sha>/check-runs` is
  authoritative in one call, and it outranks anything a brief says.

## What the brief may say, and what it may not

Anything absent from the brief is **unknown, not settled**, and any of these that is missing and matters is
asked for rather than assumed:

- the commit range or ref under review;
- whether the gates passed, at which commit, and whether the tree was clean;
- anything bypassed, and how;
- which touched files are generated rather than authored;
- the `Verify:` line of the task each commit lands under;
- the issue, record or debt entry the change claims to satisfy.

**It may not carry the implementer's reasoning** — why that shape was chosen, what alternatives were
rejected, or any self-assessment. A brief supplying it hands over a conclusion dressed as a fact.

**A false claim in the brief outranks every other finding**, and is reported first.

## Ask first whether the change moved its own goalposts

Look at what in the diff decides whether the change passes. That surface is small and
worth naming: a test's expected value, a tolerance, a test moved behind a skip marker, an `#[allow]` or a
`# type: ignore`, a lint level in the package manifest, a gate's configuration, and the `Verify:` line of
the task the commit lands under.

Touching that surface is not the finding — a tolerance is sometimes wrong, and a `Verify:` line sometimes
cannot be run as written. The finding is touching it *as the way* the task became satisfiable. Name which of
the two this diff is — a change made because the criterion was wrong, or a criterion changed because the
code would not meet it — including when it is the first, since silence here reads as not having looked.

## What to read, and what not to

Each of the four concerns against what the diff did.

- **History is not the surface.** `git log`, `git show` and `git blame` are for a commit *in the range under
  review*. What the tree used to be belongs to the records and the issue thread, so a finding needing
  archaeology to state is a finding about a record rather than about this change.
- **Read the cited section, not its file**, and a touched file rather than its neighbours.
- **A whole-tree sweep is not this review's**, and asking for one is an available verdict. The exception is
  a sweep the diff itself claims — a change asserting that no document mentions something is verified by
  running that sweep once.

## The verdict

One of three, stated outright rather than left to be inferred:

- **Accept** — nothing found, said plainly. A review that promotes a near-miss to fill the list is worse
  than a clean one.
- **Accept with findings** — each finding named, with what it costs if left. Say which are worth a commit
  now and which are worth a technical-debt entry.
- **Reject** — the change is the wrong shape, and the reason is structural rather than a matter of taste.
  Name what shape it should have had.
