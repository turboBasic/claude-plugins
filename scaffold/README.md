# modern-python

Claude Code plugin that scaffolds modern Python projects.

## Installation

```bash
claude plugin install ./
```

## Usage

### First run

```bash
mise exec -- uv run --project <plugin_dir> milestone-runner <project-name> [description] [--aws] [--output-dir DIR] [--timeout SECONDS]
```

Example:

```bash
mise exec -- uv run --project <plugin_dir> milestone-runner my-service "AWS Lambda function with httpx client" --aws --output-dir /tmp
```

The agent scaffolds the project one milestone at a time. Each milestone is verified before
moving to the next. On failure, the milestone is retried up to 3 times total.

### Resume an interrupted run

```bash
mise exec -- uv run --project <plugin_dir> milestone-runner --context /path/to/project/agent.context.json
```

Loads all context from the saved file. Already-completed milestones are skipped.

### From Claude Code (slash command)

```text
/scaffold:new-python-project <project-name> [description] [--aws]
```

### Read the log

```bash
cd /path/to/generated-project
mise exec -- uv run --project <plugin_dir> milestone-runner log-summary
# or a specific log file:
mise exec -- uv run --project <plugin_dir> milestone-runner log-summary agent-20260524T120000.log.jsonl
```

## Flags

| Flag                | Default  | Description                                      |
| ------------------- | -------- | ------------------------------------------------ |
| `project-name`      | required | name of the project to generate                  |
| `description`       | `""`     | one-line description embedded in project context |
| `--aws`             | off      | include AWS/S3 module (milestone 06)             |
| `--output-dir`      | `.`      | parent directory for the generated project       |
| `--context PATH`    | —        | resume from existing `agent.context.json`        |
| `--timeout SECONDS` | `300`    | per-milestone agent subprocess timeout           |
