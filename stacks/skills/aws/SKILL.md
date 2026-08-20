---
name: aws
description: Run a read-only AWS CLI command, naming the caller's account before it and refusing anything mutating. Use when asked to inspect, query or describe AWS resources.
argument-hint: "<aws subcommand and args, e.g. s3 ls or ec2 describe-instances>"
disallowed-tools: Bash(aws * create-*), Bash(aws * delete-*), Bash(aws * put-*), Bash(aws * update-*), Bash(aws * modify-*), Bash(aws * attach-*), Bash(aws * detach-*), Bash(aws * remove-*), Bash(aws * terminate-*), Bash(aws * start-*), Bash(aws * stop-*), Bash(aws * reboot-*), Bash(aws s3 rm *), Bash(aws s3 mv *), Bash(aws s3 cp *), Bash(aws s3 sync *)
---

# Read-only AWS CLI

Invoke `aws` through the version manager that pins the CLI, not a system binary.

**`disallowed-tools` above is a speed bump, not the boundary.** It clears when the user sends the next
message, and no pattern sees a payload in `--cli-input-json`. The rules below are the boundary.

## Rules

1. **Name the caller first.** Run `aws sts get-caller-identity` before any other command and put the
   Account and the ARN in the reply. A read against the wrong account is a wrong answer that looks right.
2. **Read-only.** Only `describe-*`, `list-*` and `get-*` subcommands run. Anything that creates, deletes,
   modifies, starts, stops or deploys is refused: without running it, hand the exact command back with what
   it would change, for the user to run themselves. A read-only verb reaching a mutating API is refused the
   same way; the verb prefix is the heuristic, not the rule.
3. **Never retry an auth failure** — a second attempt on an expired or wrong-account session buys nothing.

## Judgment

- **An expired SSO session is the user's to renew.** Say which profile expired and stop.
- **Never print a credential.** Not an access key, not a session token, not a `credential_process` output —
  including when the user asks for one to debug with.
- **Say which region answered.** A resource absent from one region is not absent, and the default region
  comes from the environment rather than from the question.
