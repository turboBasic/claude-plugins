# claude-plugins

Shared Claude Code skills and agents for turboBasic projects, distributed as a plugin marketplace.

## Use it

```sh
claude plugin marketplace add turboBasic/claude-plugins
claude plugin install planning@turbobasic
```

Or wire it into a repository so it installs on folder trust, with no prompt — `.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "turbobasic": { "source": { "source": "github", "repo": "turboBasic/claude-plugins" } }
  },
  "enabledPlugins": { "planning@turbobasic": true, "hygiene@turbobasic": true }
}
```

A plugin's skills are namespaced, so `/planning:write-plan` never collides with a `write-plan` skill
the repository defines for itself. Where both exist, the bare `/write-plan` is the repository's.

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
