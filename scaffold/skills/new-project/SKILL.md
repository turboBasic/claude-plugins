---
name: new-project
description: The file floor a repository starts with, and the order it is stood up in - context gathered and instructions written before any code. Use when creating a new project, when scaffolding one, when deciding what a fresh repository must contain, or when reading an existing repository against the baseline.
---

# A project's first commit

## Instructions before code

Gather context, write the instruction layer, then everything else. Ask about the project's purpose and
domain, its stack, whether it is solo, shared or public, and any integration or convention a reader would
not guess. **What the answers decide is written down rather than remembered** — every later change is
grounded in that file or drifts from nothing.

## The floor

| File | What it carries |
| --- | --- |
| `.editorconfig` | Indentation, line endings, charset, trailing whitespace, final newline |
| `.gitattributes` | LF normalisation and binary detection |
| `.gitignore` | The language's and the toolchain's artefacts |
| `mise.toml` | Every runtime and tool version the project assumes |
| `justfile` | At least `lint`, `test` and `fmt` |
| `.pre-commit-config.yaml` | Every linter and formatter the language needs, plus the spell checker |
| `.cspell.config.yaml` | The user dictionary where one exists, plus a project word list |
| `docs/ai-instructions.md` | The instruction layer below |
| `CLAUDE.md` | A pointer to it |
| `.github/copilot-instructions.md` | A pointer to it |

**`.editorconfig` outranks every other style statement**, including anything a skill says, so it is written
first and read before any file is.

**`prek` is the hook runner, reading `.pre-commit-config.yaml`**, and every linter, formatter and the spell
checker is a hook in it rather than a standalone script or a CI-only step. `lefthook` is the exception a
repository already holds: where `lefthook.yml` exists it stays, and a parallel `prek` config is not added
beside it. Absent an existing choice, `prek`.

**A linter is reached through the hook runner and the `justfile`, never called directly** — which is what
makes the `lint` recipe the thing CI runs too, rather than a second list of tools that drifts from it, and
what makes the hooks installable as the repository's own pre-commit gate.

## The instruction layer

`docs/ai-instructions.md` is the authoritative file, holding the project overview, the stack, the structure
tree, the code-generation rules and the behaviour guidelines. Every other AI entry point is a thin pointer
to it — `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for Copilot — so a rule has one home
and a tool-specific file never becomes a second copy.

- **The structure tree is updated in the change that adds or removes a directory**, not in a later sweep.
- **Before adding a document, check what already covers it.** Updating the owner and linking to it beats a
  parallel page, and two pages stating one fact is the failure this layer exists to prevent.

## CI

Lint, test, build, and nothing speculative. Tool versions come from the same version-manager config the
project uses locally, so a green local run means something. A third-party action is pinned to a full SHA or
an explicit tag — never `@main`; an in-house one may float. Repeated job bodies become a reusable workflow
or a composite action. Secrets arrive from the environment or OIDC and are never written into the file.

## What this does not do

- **It writes files. It creates nothing remote.** Merge methods, topics, security alerts and a protected
  default branch are the `github-repo` command's, and it is the thing to run for them.
- **A language's toolchain is its own skill** — `modern-python` for Python. This floor is what every project
  gets regardless of language.
- **Where a project template already generates the floor, run the template** and read its output against the
  table rather than writing the files by hand.
- **A single-file script is not a project.** No floor applies to one.

## Where this yields

An existing repository's conventions win over this table. Report the gap and propose it; converting a
repository's tooling, task runner or hook runner is the owner's call, not a finding to act on.
