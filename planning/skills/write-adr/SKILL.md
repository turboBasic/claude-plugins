---
name: write-adr
description: Author an architecture decision record - the bar first, so the answer may be "this belongs in the PR", then one ruling on one page. Use when asked to record or supersede an architecture decision.
---

# Write an ADR

**Acting as architect.** It owns whether a decision is worth freezing at all, and what the record rules.
It does not implement: the code that would make the ruling true is a plan's work.

The repo's instruction layer holds the bar a change must clear, the scoping rules and the line ceiling.
Absent one, the bar is that all three hold — reversing the change costs more than a PR, a competent
person would have chosen differently, and someone will ask "why is it like this?" and not be able to
answer from the code — and the ceiling is 80 lines including frontmatter. A choice a gate already pins
needs no record: the gate is the record.

**Step 1 can end the skill**, and saying so is this skill succeeding rather than refusing.

## Steps

1. **Apply the bar before drafting anything.** Answer each test out loud, on this change rather than on
   the topic it belongs to. If any fails, stop, name where the change belongs instead, and say what would
   have to become true for a record to be warranted. Do not write a short record as the compromise.
2. **Reduce it to one ruling, in one sentence, present tense.** Write that sentence first; it is the
   title and the slug. If it needs an "and" joining two independent claims, or the draft starts wanting a
   numbered list, there are two questions here: record the one asked about and name the other for its own
   record.
3. **Take the next free number** — the lowest unused four-digit prefix in `docs/decisions/`. The filename
   is that number plus a kebab-case slug of the ruling.
4. **Write the frontmatter.**

   ```yaml
   ---
   id: NNNN
   status: accepted
   date: YYYY-MM-DD
   scope: <one value from the repo's list>
   tags: [adr]
   ---
   ```

   `scope:` takes exactly one value from whatever vocabulary the repo keeps, so a record wanting two
   values is two records. A ruling no value fits adds one, to that list and in the same change — but
   check first that the want is not step 2's "and" in disguise. `superseded_by: NNNN` appears only with
   `status: superseded`; there is no `supersedes:`.
5. **Fill four sections, in this order,** under an `# ADR NNNN — <ruling>` heading.
   - **Decision.** Two to four sentences, present tense, the rule as it now stands. A reader who stops
     here can apply it. Nothing about how it is implemented.
   - **Context.** One or two paragraphs: what forced the question, and what constrains the answer.
     Context that could have been written before the problem appeared is not context. Cite inline the one
     figure that decided it; the issue holds the rest of the evidence.
   - **Options.** One `###` subsection per option actually weighed, the winner first and marked
     `(SELECTED)`, carrying `Adopted because:` and `Adopted despite:` bullets where the rest carry
     `Rejected because:` and `Rejected despite:`. **Every bullet is one line.** The winner's `despite`
     bullets are the costs taken deliberately; a loser's is its genuine merit.
   - **Consequences.** What the ruling now forbids and where the gate is, what it obliges of every future
     change in this scope, and the condition under which it would be reopened if one is knowable.
6. **Close with a Links section** naming the issue the evidence lives in, and the one or two records this
   one sits beside. Nothing else.
7. **Count the lines.** `wc -l` on the finished file, against the ceiling above. Over it, what comes out
   is a whole thing — the implementation, the evidence, or a second record — not prose tightened to fit.
8. **On supersession, edit the old record minimally** — `status: superseded`, `superseded_by: NNNN`, and
   one blockquote line under its title:

   ```markdown
   > Superseded by [ADR NNNN](NNNN-<slug>.md).
   ```

   Its four sections stay exactly as written, even where later events proved them wrong. What the new
   record replaces is a sentence in the new record's Context.
9. **Correct the instruction layer in the same change.** A record that changes a rule leaves the
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
  fix is upstream in step 2, not a better paragraph. Genuine supersession is step 8 and is rare.
- **Re-deriving an accepted record's reasoning means superseding it.** Doing neither leaves two live
  rulings on one question and no way to tell which governs.
- **A decision this repository did not make is not a record.** Upstream conventions, a language's
  defaults and a tool's behaviour are cited, not ruled on.
