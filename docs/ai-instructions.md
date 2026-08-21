# AI Instructions

## What this repository is

A Claude Code **plugin marketplace**. It distributes the skills and agents shared across turboBasic
projects, so that a skill has one home instead of a diverged copy in every repo that wanted it.

It is public: nothing here may name an internal system, a ticket key, a hostname or a team.
Work-specific skills live in a separate org-hosted marketplace.

## Layout

`.claude-plugin/marketplace.json` is the catalog, one entry per plugin. A plugin authored here has a
relative source (`./<plugin>`), holds only `plugin.json` in `.claude-plugin/`, and keeps
`skills/<name>/SKILL.md` and `agents/<name>.md` at its root. A plugin owned by another repository has
none of that: it is that repository, sourced whole, and the entry names the skill where it already
lives — [ADR 0001](decisions/0001-a-plugin-owned-elsewhere-is-the-whole-repository.md). Kebab-case for
every directory and file name.

`docs/decisions/` holds the records, `NNNN-<slug>.md`, whose `scope:` is one of `marketplace`, `plugin`
or `tooling`.

## Consumers

A consuming repo registers this marketplace in its own `.claude/settings.json` and enables the plugins
it wants. **That is a declaration, not an install:** since Claude Code 2.1.195 a plugin sourced from
another repository is fetched but stays unloaded until `claude plugin install <plugin>@turbobasic
--scope project` runs once per clone, folder trust notwithstanding.

- **Enabling is plugin-level, never skill-level, so enable narrowly.** A repo that wants one skill takes
  the whole plugin, which is why a plugin groups by workflow role and stays small — one or two per repo,
  not ten, and the skill listing's character budget truncates descriptions once too many are live.
- **A plugin skill answers to `plugin:name`.** The bare name stays the consumer's own copy, so a repo
  whose conventions differ keeps a local skill that wins the short command.

## Agents

An agent file holds a persona's stance; a skill holds a procedure. Five parts, in order: an untitled
stance — what it owns, what it refuses; the conclusion available to it and why its fresh context makes it
available; `## What it measures against`; `## Method`; `## Output`, pointing at the owning skill.

**A read-only agent omits `Edit`, `Write` and `NotebookEdit`** — a speed bump, since it keeps `Bash`.

## Invariants

- **A plugin authored here groups by workflow role, not by tech stack.** A skill that belongs to no role
  is a sign the role set is wrong, not that a plugin needs a grab bag. **`stacks` is the deliberate
  exception:** its skills answer to a tool, and it is enabled only in the repos holding that tool. A stack
  skill that fits a role goes to that role; a third that fits none retires the exception rather than
  extending it. A plugin owned by another repository is outside this rule rather than an exception to it —
  it is named for that repository, and nothing here composed it.
- **A plugin's skill is generic.** The moment it names one consumer's conventions — a path, a ceiling, a
  label scheme — it belongs in that consumer's own `.claude/skills/` instead.
- **Generic is not unconditional: a plugin states the substrate it assumes.** `planning` assumes GitHub
  issues and pull requests — `write-plan` starts from an issue and ticks its checkboxes, `write-issue` and
  `groom-milestone` have no subject without them, and `run-plan` treats the plan file as scratch because
  the issue is the durable half. **A repo with no remote enables none of it**, and its own skills are not
  a diverged copy to reconcile but the only ones that fit.
- **Every `plugin.json` carries a `version`, and the marketplace entry does not repeat it.** Bump it when
  a change should reach consumers, not on every edit.
- **A plugin whose source is another repository is that repository, never copied in here**, so it stays
  where it is edited: a `url` source over HTTPS at `ref: main`, `strict: false`, naming its skill at
  `./.claude/skills/<name>`, and carrying no `version` so the resolved commit is the version. Not
  `git-subdir`, and not a `github` source — [ADR 0001](decisions/0001-a-plugin-owned-elsewhere-is-the-whole-repository.md)
  rules on why, and an install rather than `mise run ci` is what evidences one.
- **A citation between two plugins here is namespaced `plugin:name`, and it makes the cited plugin a
  dependency.** A consumer enabling the citing plugin alone gets a dead citation, so the pairing belongs
  in the enablement advice rather than being discovered per repo. Live: `planning:run-plan` reviews a
  phase as `review:architect` and gates phase completion on answering its findings, so **`planning`
  requires `review`.**
- **A fact has one home, and pointers to it never round-trip.**
- **An agent's `tools:` is an allowlist; a skill's `allowed-tools` is not.** An agent that cites a skill
  lists `Skill` or the citation is dead. An unlisted command in a skill still runs, so a prohibition the
  skill relies on is prose in its body.

## Working style

`mise run ci` is the gate; run it before reporting work done — nothing is installed globally.

The `claude-code-guide` agent owns Claude Code's own formats; ask it rather than guessing a field name.

## Prose

A skill's body is loaded into a live context, so length is a running cost rather than a style
question. Say what the procedure is; do not explain why it exists, restate what a step obviously
does, or narrate what the skill used to be. `git log` owns history.
