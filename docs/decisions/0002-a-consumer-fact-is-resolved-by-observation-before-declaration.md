---
id: 0002
status: accepted
date: 2026-08-23
scope: marketplace
tags: [adr]
---

# ADR 0002 — A consumer fact is resolved by observation before declaration

## Decision

A plugin skill needing a consumer-specific fact takes the first answer of four rungs, in order: the
artefact in the consumer's repository that already owns the fact, read by a command the skill names;
the consumer's **declaration** of it — a key in an optional `.claude/conventions.json`, or the fact
where their instruction layer already states it; the default the skill itself states; and asking.
Where the fact has no safe default, the skill names which rung answered it. A fact reaching the
fourth rung where nobody can be asked stops the run rather than defaulting.

**First answer wins for a location or an existing value; for a vocabulary or a limit the artefact is
a floor** — what a repository has used is not what it permits, so later rungs widen it, not skip it.

## Context

The skills across `planning`, `review` and `hygiene` defer their consumer facts to "the repo's
instruction layer" — a phrase naming no file, no search order and no stopping rule, so absence is
indistinguishable from a failure to look. The cost is measurable in the marketplace's own prose:
`run-plan` step 7 defaults the gate to `prek run --all-files` then `mise run ci`, while
`housekeeping` check 1 defaults that same fact to the task runner's `ci` target, else `lint`, else
the hook runner — two homes and two answers for one fact, which `update-docs` step 2 calls a repeat.
The ADR `scope:` vocabulary and the debt register have no default at all, so `write-adr` step 4
invents a taxonomy silently and differently each run.

What constrains the answer is that a consumer's `docs/ai-instructions.md` cannot be given an
enforced structure, and reaches a skill only where their `CLAUDE.md` references it. Observation is
unconditional by comparison. What fixed the order is that observation was already the reflex in the
best-reasoned block here — `groom-milestone`'s "GitHub mechanics" table reads each fact with a `gh`
call rather than describing it — and was never stated as the rule.

## Options

### The four-rung ladder, observation first (SELECTED)

- Adopted because: a fact's owner is usually an artefact already there, needing no consumer action.
- Adopted because: a command and a key answer unconditionally, where loaded prose depends on a `@`.
- Adopted because: it applies the rule that a gate owns what it enforces, prose only linking to it.
- Adopted despite: four rungs are more to author per fact than one lookup.
- Adopted despite: rung 1 spends a command per fact where prose spends nothing.

### A required assertive form in `docs/ai-instructions.md`

- Rejected because: a fixed prose form is a structure, and structure is what cannot be enforced.
- Rejected because: prose would then own a value an artefact owns, which `update-docs` forbids.
- Rejected despite: prose is rung 2 where it states the fact — what loses is requiring a form.

### `repo.toml` as the only channel, ahead of observation

- Rejected because: it declares what is observable — consumers restate what the repo already states.
- Rejected because: a repo without the file loses every fact, including those rung 1 would answer.
- Rejected despite: being rung 2 itself, which is adopted where no artefact can be observed.

## Consequences

A skill may no longer state a consumer's value where an artefact holds it; it names the command
that reads it instead, and naming a command or a key is not "naming one consumer's convention"
under the generic-skill invariant. Every fact a new skill defers carries either a rung-1 command or
a key and a default, and a fact with no safe default carries the clause naming the rung that
answered it. `.claude/conventions.json` is rung 2's home, optional, and it gains a key when a fact
needs one, not now.

No gate pins any of this; `mise run ci` reads files and runs nothing a plugin ships. The evidence is
the gate command: neither skill states a value for it now. Both still name the command that reads
it, since citing across plugins would make one a dependency.

Reopen if an artefact is found to state a value its repository does not follow.

## Links

- [Issue #15](https://github.com/turboBasic/claude-plugins/issues/15) — the facts catalogued.
- [ADR 0001](0001-a-plugin-owned-elsewhere-is-the-whole-repository.md) — the sibling ruling.
