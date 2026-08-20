---
name: aws
description: Run a read-only AWS CLI command, naming the caller's account before it and refusing anything mutating. Use when asked to inspect, query or describe AWS resources.
argument-hint: "<aws subcommand and args, e.g. s3 ls or ec2 describe-instances>"
disallowed-tools: Bash(aws * create-*), Bash(aws * delete-*), Bash(aws * put-*), Bash(aws * update-*), Bash(aws * modify-*), Bash(aws * attach-*), Bash(aws * detach-*), Bash(aws * remove-*), Bash(aws * terminate-*), Bash(aws * start-*), Bash(aws * stop-*), Bash(aws * reboot-*), Bash(aws s3 rm *), Bash(aws s3 mv *), Bash(aws s3 cp *), Bash(aws s3 sync *)
---

# Read-only AWS CLI

Invoke `aws` through the repo's pinned toolchain rather than a system binary — the `lint`-style entry point
where the repo defines one, otherwise the version manager it pins the CLI with.

**`disallowed-tools` above is a speed bump, not the boundary.** Its patterns match anywhere in the command
string, so they do catch a verb inside a subcommand — `aws s3api delete-object` is denied. What they cannot
catch is a mutating verb no pattern names, a payload passed through `--cli-input-json`, or a command
assembled in a shell variable. They also clear when the user sends the next message, while these rules hold
for the session. The three rules below are the boundary, and they hold because this skill follows them.

## Rules

1. **Name the caller first.** Run `aws sts get-caller-identity` before any other command and put the
   Account and the ARN in the reply. A read against the wrong account is a wrong answer that looks right.
2. **Read-only.** Only `describe-*`, `list-*` and `get-*` subcommands run. Anything that creates, deletes,
   modifies, starts, stops or deploys is refused — hand the exact command back for the user to run
   themselves, with what it would change:

   > This command mutates infrastructure and is not run automatically. Review the impact and run it
   > yourself: `<command>`

   A read-only verb reaching a mutating API is refused the same way; the verb prefix is the heuristic, not
   the rule.
3. **Never retry a failure.** Report the error and stop. A failed call may already have landed a side
   effect, and a second attempt on an expired or wrong-account session buys nothing.

## Judgment

- **An expired SSO session is the user's to renew.** Say which profile expired and stop; a login cannot be
  driven from here.
- **Never print a credential.** Not an access key, not a session token, not a `credential_process` output —
  including when the user asks for one to debug with.
- **Say which region answered.** A resource absent from one region is not absent, and the default region
  comes from the environment rather than from the question.
