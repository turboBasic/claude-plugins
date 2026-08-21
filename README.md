# claude-plugins

Shared Claude Code skills and agents for turboBasic projects, distributed as a plugin marketplace.

## Use it

```sh
claude plugin marketplace add turboBasic/claude-plugins
claude plugin install planning@turbobasic
```

Or wire it into a repository — `.claude/settings.json`, naming only the plugins that repository needs:

```json
{
  "extraKnownMarketplaces": {
    "turbobasic": { "source": { "source": "github", "repo": "turboBasic/claude-plugins" } }
  },
  "enabledPlugins": { "planning@turbobasic": true, "hygiene@turbobasic": true }
}
```

**That file is a declaration, not an install.** Since Claude Code 2.1.195 a plugin sourced from another
repository is fetched but not loaded until someone installs it, so each one needs a single command per
clone — trusting the folder is not enough:

```sh
claude plugin install planning@turbobasic --scope project
```

A plugin's skills are namespaced, so `/planning:write-plan` never collides with a `write-plan` skill
the repository defines for itself. Where both exist, the bare `/write-plan` is the repository's.

## Documentation lookups

`1password-docs`, `aws-sso-cli-docs`, `chezmoi-docs`, `mise-docs`, `uv-docs` and `zinit-docs` are not
held here — each is the documentation repository of that tool, published from where it is edited, and
each answers to `<plugin>:<tool>` (`/chezmoi-docs:chezmoi`). They carry their own knowledge base, so
`/plugin marketplace update` is what picks up a documentation change.

## Work on it

```sh
mise run setup    # git hooks
mise run lint     # markdownlint, cspell, taplo, manifest checks
mise run ci       # what CI runs
```

Test a change before it is published by adding the working tree as a marketplace:

```sh
claude plugin marketplace add .
```

See [`docs/ai-instructions.md`](docs/ai-instructions.md) for what belongs here and what does not.
