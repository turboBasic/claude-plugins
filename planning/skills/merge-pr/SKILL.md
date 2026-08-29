---
name: merge-pr
description: Merge the open pull request for the current branch through GitHub with gh, squashing by default or rebasing on request. Use when asked to merge, squash-merge, rebase-merge or land a PR.
argument-hint: [squashing|rebasing all commits as is]
model: sonnet
allowed-tools: Bash(git log:*), Bash(git diff:*), Bash(gh pr view:*), Bash(gh pr merge:*)
---

# Merge a PR

Merges through GitHub, never locally.

1. **Resolve the PR.** `gh pr view --json number,url,baseRefName,mergeStateStatus`. No open PR for
   this branch: say so, stop. `mergeStateStatus` of `DIRTY` or `BLOCKED`: report why, stop — never
   force through a failing check, an unresolved review thread or a conflict.

2. **Pick the mode from the invocation's prose**, default squash:
   - Says to rebase, keep commits as is, or preserve history → **rebase**.
   - Says to squash, or says nothing about mode → **squash**.

3. **Rebase mode** — `gh pr merge --rebase`. Commits already read as intended, no message to write.

4. **Squash mode** — `gh pr merge --squash --subject "<title>" --body "<summary>"` (note
   `--subject`, not `--title`). The body summarizes the net change across every commit and the full
   diff, not a commit-by-commit log. Derive the title as Conventional Commits, imperative, no
   trailing period, at most 72 characters: all commits sharing a type and scope, use them; types
   spanning several, take the dominant one, preferring `feat` over `fix` over the rest; scopes
   spanning several, omit the scope.

5. Report the resulting commit and whether the base branch fast-forwarded.

## Rules

- **Squash body is a summary, not a changelog.** No invented change, nothing not covered by the
  diff.
- **Nothing is committed, amended or pushed here.** The branch is taken as it stands.
