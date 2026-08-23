# Technical debt

A shortcut this repository took knowingly, held here because it is not work anyone will pick up as it
stands. Work someone will do is an issue; a ruling is a record under `docs/decisions/`.

An entry earns its place by stating a **condition the repository can answer**, so that a sweep can call it
due or not without asking anyone. "Revisit whether a plugin has grown too big" cannot be answered; "a
third stack enters `scaffold`" can. An obligation that resists such a condition belongs in an issue instead.

`TD-NN` is the identifier, assigned in order and never reused. A plan's Technical debt section, an ADR's
consequences and a review finding all cite it by that identifier alone.

## How the sweep reads this

`hygiene:housekeeping` check 4 evaluates every entry's **Due when** against the tree and reports the ones
that now hold. It does not edit this file. An entry whose condition holds is paid by doing the work and
deleting the row — a paid entry leaves no tombstone, because `git log` owns that.

## Entries

| ID | Debt | Due when | Costs if left |
|---|---|---|---|
| — | No entries. | — | — |
