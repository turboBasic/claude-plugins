# AI Instructions

## What this repository is

A Claude Code **plugin marketplace**. It distributes the skills and agents shared across turboBasic
projects, so that a skill has one home instead of a diverged copy in every repo that wanted it.

It is public: nothing here may name an internal system, a ticket key, a hostname or a team.
Work-specific skills live in a separate org-hosted marketplace.

## Layout

`.claude-plugin/marketplace.json` is the catalog, one entry per plugin, sources relative as
`./<plugin>`. Inside a plugin only `plugin.json` lives in `.claude-plugin/`; `skills/<name>/SKILL.md`
and `agents/<name>.md` sit at the plugin root. Kebab-case for every directory and file name.

## Consumers

A consuming repo registers this marketplace in its own `.claude/settings.json` and enables the plugins
it wants.

- **Enabling is plugin-level, never skill-level.** A repo that wants one skill takes the whole plugin,
  which is why a plugin groups by workflow role and stays small — one or two per repo, not ten.
- **A plugin skill answers to `plugin:name`.** The bare name stays the consumer's own copy, so a repo
  whose conventions differ keeps a local skill that wins the short command.
- **Enable narrowly.** The skill listing has a character budget, and descriptions truncate once too many
  skills are live.

## Agents

An agent file holds a persona's stance; a skill holds a procedure. Five parts, in order: an untitled
stance — what it owns, what it refuses; the conclusion available to it and why its fresh context makes it
available; `## What it measures against`; `## Method`; `## Output`, pointing at the owning skill.

**A read-only agent omits `Edit`, `Write` and `NotebookEdit`** — a speed bump, since it keeps `Bash`.

## Invariants

- **Plugins group by workflow role, not by tech stack.** A skill that belongs to no role is a sign the
  role set is wrong, not that a plugin needs a grab bag. **`stacks` is the single exception, taken
  deliberately:** its skills answer to a tool rather than a role, and the alternatives were a grab-bag
  role plugin or leaving the copies diverged. It earns the carve-out by being enabled only in the repos
  holding that tool, which is what "Enable narrowly" asks of any plugin anyway. A stack skill that does
  fit a role goes to that role; a third that fits none retires the exception, and `stacks` is
  reconsidered rather than extended.
- **A plugin's skill is generic.** The moment it names one consumer's conventions — a path, a ceiling, a
  label scheme — it belongs in that consumer's own `.claude/skills/` instead.
- **Every plugin entry carries a `version`.** Bump it when a change should reach consumers, not on every
  edit.
- **A plugin whose source is another repository is listed with `git-subdir`, never copied in here**, so
  that repository stays where it is edited. Pinned to `ref: main`, its commit is the version.
- **A citation between two plugins here is namespaced `plugin:name`.**
- **A fact has one home, and pointers to it never round-trip.** `write-issue` cites `groom-milestone` for
  the GitHub endpoints, so `groom-milestone` does not cite it back.
- **An agent's `tools:` is an allowlist; a skill's `allowed-tools` is not.** An agent that cites a skill
  lists `Skill` or the citation is dead. An unlisted command in a skill still runs, so a prohibition the
  skill relies on is prose in its body.

## Working style

`mise run ci` is the gate; run it before reporting work done. It wraps `prek`, and nothing is installed
globally.

The `claude-code-guide` agent owns Claude Code's own formats; ask it rather than guessing a field name.

## Prose

A skill's body is loaded into a live context, so length is a running cost rather than a style
question. Say what the procedure is; do not explain why it exists, restate what a step obviously
does, or narrate what the skill used to be. `git log` owns history.
