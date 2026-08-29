# Technical debt

A shortcut this repository took knowingly, held here because nobody will pick it up as it stands. Work
someone will do is an issue; a ruling is a record under `docs/decisions/`.

An entry states a **condition the repository can answer**, so a sweep can call it due without asking
anyone — "a second consumer needs the same override" can be answered, "revisit whether this got too
big" cannot, and an obligation that resists such a condition belongs in an issue. `TD-NN`, assigned in
order and never reused, is how a plan, an ADR or a review finding cites an entry; a paid entry is the
work done and the row deleted, so `git log` holds the highest number assigned.

## Entries

| ID | Debt | Due when | Costs if left |
|---|---|---|---|
| TD-01 | Shipped Python has no typecheck. `ruff` lints `scaffold/scripts/repo_settings.py`; nothing checks the shape of the payloads it builds. | A second plugin here ships a script — one typecheck then covers two hooks' worth of surface instead of one file, per [ADR 0002](decisions/0002-a-plugin-may-ship-one-dependency-free-script.md). | A wrong payload shape reaches the GitHub API before anything complains, and the failure is a 422 in a consumer's shell rather than a red gate here. |
