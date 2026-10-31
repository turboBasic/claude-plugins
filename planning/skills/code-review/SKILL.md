---
name: code-review
description: Review changed code against repository conventions, naming and SOLID principles. Use after a change is complete and ready for review, or when asked whether code meets project standards.
---

# Review code

Judge whether the changed code meets the repository's standards. Do not implement; return findings to
whoever owns the tree. A review may report only minor issues or no findings.

## What to measure

- Follow the tree's conventions, whether written or established by nearby code. Where those disagree
  with a general principle, the tree's convention wins.
- Use grammatical, unambiguous names that reflect domain concepts.
- Cite the SOLID principle by name where one is broken; do not restate it.

## Method

- Review the changed code, not the whole codebase. Read touched files and only the surrounding files
  needed to establish a convention.
- Check a name against its siblings by searching for the existing naming pattern.
- Name the file and line for every finding. If it cannot be located, omit it.
- Give a concrete improvement, with a short code example when that is clearer.

## Output

- Findings, architectural violations first, with location, violated principle or convention, and a
  concrete improvement.
- Overall assessment and what to address first.
- Strengths worth keeping.
