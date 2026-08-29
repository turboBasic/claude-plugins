---
name: open-pr
description: Open a pull request for the current branch with gh, filling the repo's PR template from the diff. Use when asked to create, open or raise a PR.
model: sonnet
allowed-tools: Bash(git log:*), Bash(git diff:*), Bash(git rev-parse:*), Bash(git branch:*), Bash(git checkout:*), Bash(git push:*), Bash(gh pr create:*), Bash(gh pr view:*), Bash(gh repo view:*), Read
---

# Open a PR

Merging is `merge-pr`'s; reviewing the change is `review-change`'s.

1. **Resolve the default branch** via `gh repo view --json defaultBranchRef -q .defaultBranchRef.name`,
   then collect the log and diff of `HEAD` against it. Nothing unmerged, or `gh pr view` finding a PR
   already open on the branch: report that and stop.

2. **Determine the feature branch.** On a branch that is not `$BASE`, use it as is. On `$BASE`,
   derive a name from the most representative commit subject — strip the Conventional Commits
   prefix, lower-case, replace anything non-alphanumeric with `-`, truncate to 50 characters, and
   re-prefix with the type as a directory: `feat(ci): add actionlint hook` →
   `feat/add-actionlint-hook`. Then `git checkout -b <name> && git push -u origin <name>`.

3. **Read `.github/PULL_REQUEST_TEMPLATE.md` verbatim.** That is the skeleton, its sections are the
   only sections, and every one of them and every placeholder gets filled.

4. **Derive the title** as `merge-pr` derives its squash title.

5. **Open the PR** with `gh pr create`, passing `--repo`, `--base` and `--head` explicitly — omit
   any of them and `gh` prompts interactively, and the run stalls. Report the URL it returns.

## Rules

- **Nothing that is not in the diff.** No invented change.
- **Drop the template's authoring prompts once answered; keep any comment addressed to a machine** —
  a bot directive, a release-note marker, a `do not remove`.
- Plain `-` bullets in the changes list, never numbered.
- **Commit nothing and amend nothing.** The branch is taken as it stands.
