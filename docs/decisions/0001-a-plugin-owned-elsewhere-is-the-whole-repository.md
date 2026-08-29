---
id: 0001
status: accepted
date: 2026-08-21
scope: marketplace
---

# ADR 0001 — A plugin owned elsewhere is the whole repository, sourced over HTTPS

## Decision

A skill that belongs to another repository is published as its own plugin, one per repository, whose
source is that whole repository fetched over HTTPS at its main branch. The entry names the skill at the
path it already occupies and requires no manifest there, so the source repository is never edited and a
sibling skill the entry does not name stays unpublished. It pins no version: the resolved commit is the
version.

## Context

The six documentation lookups — chezmoi, mise, uv, zinit, 1Password, aws-sso-cli — each live in the
repository whose tool they document, and each greps a `cards/` knowledge base that sits at that
repository's root, above the skill's own directory. Publishing them had to reach both the skill and
the base without copying either here.

`git-subdir`, which this repository's instruction layer required, cannot: it is a sparse fetch of the
named path alone, so `cards/` never arrives. A source must also resolve to a plugin root rather than a
`SKILL.md` directory, and one entry takes one source — so no single plugin spans six repositories. A
whole-repo source reproduces the repository layout in the cache, which is why the skills' existing
`${CLAUDE_SKILL_DIR}/../../../cards/` resolves untouched; the largest of the six is 2.1 MB installed.

## Options

### Whole repository per repository, over HTTPS (SELECTED)

- Adopted because: the only shape that delivers the skill and the knowledge base above it together.
- Adopted because: no doc repository is edited, and none gains a manifest it has no other use for.
- Adopted despite: six plugins to enable rather than one, against the listing budget.
- Adopted despite: shipping each repository whole, including its docs source and history.

### One bundled `docs-lookup` plugin holding copies

- Rejected because: one entry takes one source, so the six skills would have to be copied in here.
- Rejected because: a copy leaves the knowledge base behind, and a second home for a skill to drift in.
- Rejected despite: one namespace and one thing for a consumer to enable.

### `git-subdir` at the skill's directory

- Rejected because: the sparse fetch excludes `cards/`, and the path is not a plugin root.
- Rejected despite: fetching kilobytes where the selected shape fetches megabytes.

### A `github` source rather than `url`

- Rejected because: it clones over SSH, and this account reaches GitHub over HTTPS — an access property.
- Rejected despite: `owner/repo` shorthand, and `marketplace add` falling back to HTTPS on its own.

## Consequences

Copying an externally owned skill into this repository is now closed, and so is `git-subdir` for any
skill whose knowledge base sits above it. Every entry of this kind names its skill path explicitly and
omits `version`, so a documentation change reaches consumers through `/plugin marketplace update`
alone. No gate pins any of this — `mise run ci` checks only that the manifests parse and name
themselves — so the evidence is an install: the skill listed under `<plugin>:<tool>`, the cache
directory named for the commit, and the base beside it.

Reopen if a fetch mode appears that can carry a sibling path, or if a source repository grows a
`plugin.json` of its own for another reason.

## Links

- [PR #3](https://github.com/turboBasic/claude-plugins/pull/3) — the six entries and the install evidence.
