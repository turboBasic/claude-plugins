---
name: github-repo
description: Apply the GitHub repository baseline — merge methods, feature toggles, topics, security alerts and a protected default branch, creating it first on request.
---

# Apply the GitHub repository baseline

Assumes `gh` is authenticated as the owner, `python3` 3.7 or later is on `PATH`, and the user
provided a repository name or `owner/name`.

Run the bundled `../../scripts/repo_settings.py` (resolved from this skill's directory) with the
user's arguments unchanged. The script owns the baseline, flags and order of API calls; add nothing
and decide nothing it decides. Read its output:
each `key: was -> will be` line, then whether it applied, was a dry run, or had nothing to change.
Report a non-zero exit as it stands.

`gh api` by hand is not a fallback. Report a failed run without finishing it manually or retrying
under different flags.
