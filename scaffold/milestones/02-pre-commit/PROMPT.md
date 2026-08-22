# pre-commit

**! This file is ignored, milestone type = "generated" !**

Install and configure pre-commit with ruff, Pyright, and standard hooks.

Context keys: `package_name`

## Constraints

- Write `<latest>` as the `rev` placeholder for every repo — never hardcode version strings before running `pre-commit autoupdate`.

## Steps

1. **file** — `.pre-commit-config.yaml`
   Write with `<latest>` as the `rev` placeholder for every repo — the next step resolves them.
   Include these hooks:
   - `https://github.com/astral-sh/ruff-pre-commit` — ruff linter and formatter
   - local hook: `pyright` — run via `mise exec --`, do not pass filenames
   - `https://github.com/adrienverge/yamllint`
   - `https://github.com/shellcheck-py/shellcheck-py`
   - `https://github.com/rhysd/actionlint`
   - `https://github.com/compilerla/conventional-pre-commit` — commit-msg stage

2. **command** — `mise exec -- pre-commit autoupdate`
   Resolves every `<latest>` rev placeholder to the current release tag.
   Requires `pre-commit` to be installed via mise — add it to `mise.toml` first (step 3) if not present.
   Note: run this AFTER writing `.pre-commit-config.yaml` but check mise.toml first.
   **Fallback:** if resolution fails for a hook, keep the existing `<latest>` placeholder and report the hook name in `notes`.

3. **file** — update `mise.toml`
   Add `pre-commit = "latest"` to `[tools]` if not already present.
   Preserve all existing content.

4. **file** — update `justfile`
   Replace the `lint` recipe body with `mise exec -- pre-commit run --all-files`.
   Add a `hooks` recipe: `mise exec -- pre-commit install --install-hooks`.
   Preserve all other recipes unchanged.

## Notes

Each bullet below becomes one string in the `notes` array (2 entries expected):

- Resolved version tag for each hook repo (e.g. `ruff-pre-commit@v0.11.0`)
- Any hooks that `pre-commit autoupdate` failed to resolve (fallback version used)
