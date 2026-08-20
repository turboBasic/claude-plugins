---
name: update-docs
description: Consolidate existing documentation onto one owner per fact and resolve what contradicts - editing what is there, never adding a document. Use when asked to audit, tidy, consolidate or de-duplicate the docs.
---

# Consolidate the docs

**Acting as architect.** It owns which file owns a fact. It does not author: a gap this sweep finds is
reported, and filling it is its own work.

**This skill edits; reporting without editing is `hygiene:housekeeping`'s sweep**, which cites step 2's test.

**No new file, and no new section**, unless the invocation names one to create.

## Steps

1. **Inventory** every document in the repo — the README, `docs/`, the instruction layer, and doc comments
   carrying prose a document also carries.
2. **Find the overlaps**: statements that contradict each other across files, and repeats — delete a
   sentence mentally, and if neither a route nor a fact is lost it is a repeat. Restatement is sanctioned in
   an invariant list, a decision record that decided the fact, and the human-facing layer; a hit in the
   human layer counts only when it contradicts its owner or pins an enforcement detail.
3. **Name one owner per overlapping topic** — the most authoritative location, which is the one a reader
   would reach for first, not the longest treatment. Replace every other copy with a link to it.
4. **Resolve each contradiction toward the code**, not toward the better-written sentence. Where the code
   and configuration answer it, they decide; where they do not, it is a judgment and goes in the report.
5. **Leave the content you cannot verify.** Flag it.
6. **Report** the changed files with one line each, what was consolidated onto which owner, and the
   ambiguities left for a human.

## Judgment

- **Structure stays as written** unless changing it is what removes the duplication.
- **A pointer never round-trips.** Where A cites B for a fact, B does not cite A back for it; two files
  pointing at each other own nothing between them.
- **A gate is the owner of what it enforces.** Prose restating a lint level, a pinned version or a
  threshold is a finding, and the fix is a link to the config file rather than a corrected number.
