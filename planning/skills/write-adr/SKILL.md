---
name: write-adr
description: Author an architecture decision record - the bar first, so the answer may be "this belongs in the PR", then one ruling on one page. Use when asked to record or supersede an architecture decision.
---

# Write an ADR

**Acting as architect.** It owns whether a decision is worth freezing at all, and what the record rules.
It does not implement: the code that would make the ruling true is a plan's work.

## The bar

**The trigger is a question, not a work package.** Most issues warrant no record; one may warrant two,
having raised two independent questions; and a question raised in conversation with no issue behind it
warrants one just the same.

A change is recorded only when all three hold:

1. **Reversing it costs more than a PR.** It crosses a boundary something outside the change depends on,
   changes a published format, or changes a project-wide policy.
2. **A competent person would have chosen differently.** There was a real option, not a preference.
3. **Someone will ask "why is it like this?" and not be able to answer from the code.**

A record clearing it rules the constraint rather than the implementation of it, and enumerates no schema,
field list or layout — state the property the artefact must have. Decomposition is not a record: the steps
live in an issue and a plan file.

- **A choice a gate already pins needs no record: the gate is the record.**
- **A record whose own Consequences say it is cheap to reverse has failed test 1.**

**One page — 80 lines including frontmatter, hard.** Not a style preference: it forces the rules above it.

## Steps

1. **Apply the bar before drafting anything.** Answer each test out loud, on this change rather than on
   the topic it belongs to. If any fails, stop, name where the change belongs instead, and say what would
   have to become true for a record to be warranted — **ending here is this skill succeeding rather than
   refusing**. Do not write a short record as the compromise.
2. **Reduce it to one ruling, in one sentence, present tense.** Write that sentence first; it is the
   title and the slug. If it needs an "and" joining two independent claims, or the draft starts wanting a
   numbered list, there are two questions here: record the one asked about and name the other for its own
   record.
3. **Take the number after the highest ever used** — never a gap, which `git log --diff-filter=D
   --name-only` explains — in the directory the records sit in, `rg --files -g '[0-9][0-9][0-9][0-9]-*.md'`,
   `docs/decisions/` absent any. Plus a kebab-case slug of the ruling.
4. **Write the frontmatter.**

   ```yaml
   ---
   id: NNNN
   status: accepted
   date: YYYY-MM-DD
   scope: <one value from the repo's list>
   ---
   ```

   `date:` is `date -I`, never a date from memory. `status:` is `accepted` or `superseded`, and nothing
   else. `rg '^scope:'` over that directory names what past records used, and the
   instruction layer names whatever else it permits; **no default — absent both, ask.** A ruling no value
   fits adds one, to that list and in the same change, but check first that the want is not step 2's "and"
   in disguise.
5. **Fill five sections, in this order,** under an `# ADR NNNN — <ruling>` heading.
   - **Decision.** Two to four sentences, present tense, the rule as it now stands. A reader who stops
     here can apply it.
   - **Context.** One or two paragraphs: what forced the question, and what constrains the answer.
     Context that could have been written before the problem appeared is not context. Cite inline the one
     figure that decided it; the issue holds the rest of the evidence.
   - **Options.** One `###` subsection per option actually weighed, the winner first and marked
     `(SELECTED)`, carrying `Adopted because:` and `Adopted despite:` bullets where the rest carry
     `Rejected because:` and `Rejected despite:`. **Every bullet is one line.** The winner's `despite`
     bullets are the costs taken deliberately; a loser's is its genuine merit.
   - **Consequences.** What the ruling now forbids and where the gate is, what it obliges of every future
     change in this scope, and the condition under which it would be reopened if one is knowable.
   - **Links.** Where the evidence lives — an issue, else the PR, else "no issue" said outright — and the
     one or two live records this one sits beside. Nothing else.
6. **Count the lines.** `wc -l` on the finished file, against the ceiling above. Over it, what comes out
   is a whole thing — the implementation, the evidence, or a second record — not prose tightened to fit.
7. **On supersession, edit the old record minimally** — `status: superseded`, `superseded_by: NNNN` and no
   `supersedes:` on the new one, and one blockquote line under the old title:

   ```markdown
   > Superseded by [ADR NNNN](NNNN-<slug>.md).
   ```

   Its sections stay exactly as written, even where later events proved them wrong. What the new record
   replaces is a sentence in the new record's Context.

   **A ruling that was a mistake rather than a stage is deleted, not tombstoned** — `git log` owns that it
   existed, and step 8 applies to whatever of the rule still holds.
8. **Correct the instruction layer in the same change.** A record that changes a rule leaves the
   instruction layer stating the old one. The rule goes there in present tense with a one-line link here
   for the why; neither restates the other at length.

## Judgment

- **"This belongs in the PR" is the most common correct answer, and it is worth saying well.** Name the
  target rather than declining: the PR description, a comment beside the configuration, a sentence in the
  instruction layer, a test that pins the tolerance, a technical-debt entry, or nothing at all. A choice
  with a demotion target named is settled; a choice merely refused a record comes back.
- **The options are the ones actually weighed.** Padding with plausible rejects tells a later reader an
  option was examined when nothing was learned about it. The option the user first proposed belongs there
  by name whenever it lost.
- **A draft that opens by positioning itself against another record is reporting a scoping error.** The
  fix is upstream in step 2, not a better paragraph. Genuine supersession is step 7 and is rare.
- **Re-deriving an accepted record's reasoning means superseding it.** Doing neither leaves two live
  rulings on one question and no way to tell which governs.
- **A decision this repository did not make is not a record.** Upstream conventions, a language's
  defaults and a tool's behaviour are cited, not ruled on.
