# ci

**! This file is ignored, milestone type = "generated" !**

Add GitHub Actions CI workflow with lint and test jobs, Dependabot, and Renovate config.

Context keys: `project_name`, `package_name`

## Constraints

- Pin all actions to exact version tags (e.g. `actions/checkout@v4.2.2`), never to branch names.

## Steps

1. **command** — `mkdir -p .github/workflows`

2. **resolve action versions** — before writing `ci.yml`, query the GitHub API for the latest
   release tag of each action you intend to use:
   `https://api.github.com/repos/<owner>/<repo>/releases/latest`
   Use the returned `tag_name` as the pinned version (e.g. `actions/checkout@v4.2.2`).
   **Fallback:** if a query fails or returns no tag, use a recent known version and add the action name to `notes`.

3. **file** — `.github/workflows/ci.yml`
   Two jobs: `lint` and `ci`. Requirements:
   - Trigger on `push` and `pull_request` to `main`.
   - Both jobs: `actions/checkout`, `jdx/mise-action` (installs all tools from `mise.toml`).
   - `lint` job: runs `mise exec -- pre-commit run --all-files` on push;
     on pull_request uses `tj-actions/changed-files` to get changed files and passes them
     to `mise exec -- pre-commit run --files $FILES`.
   - `ci` job: runs `mise exec -- just type-check` then `mise exec -- just test`.
   - Cache `~/.cache/uv` keyed on `uv.lock` hash in the `ci` job.
   - Cache `~/.cache/pre-commit` keyed on `.pre-commit-config.yaml` hash in the `lint` job.

4. **file** — `.github/dependabot.yml`
   Enable for `github-actions` and `pip` ecosystems.
   Set `open-pull-requests-limit: 0` on both — security updates only, no routine bumps.

5. **file** — `.github/renovate.json`

   ```json
   { "$schema": "https://docs.renovatebot.com/renovate-schema.json", "extends": ["config:recommended"] }
   ```

## Notes

Each bullet below becomes one string in the `notes` array (2 entries expected):

- Resolved version tag for each GitHub Action used (e.g. `actions/checkout@v4.2.2`)
- Any action versions that fell back to a hardcoded value because the API query failed
