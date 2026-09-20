---
name: terraform
description: Hold Terraform to one shape - snake_case names, providers pinned, a flat module layout - and keep state and the apply out of the assistant's hands. Use when writing or modifying a .tf file, when laying out a Terraform configuration, or when asked to run Terraform.
---

# Terraform shape

Applies to every `.tf` and `.tfvars` file written or touched.

## State and apply are the user's

**Never touch state files or backend configuration without explicit instruction.** No `terraform state`
subcommand, no edit to a `.tfstate`, no change to a `backend` block — a wrong move there orphans real
infrastructure from the configuration that is supposed to own it, and the damage outlives the session.

**`fmt`, `validate` and `plan` run freely. `apply`, `destroy`, `import` and `taint` do not:** hand the exact
command back with what the plan says it would change, for the user to run. An `apply` the user did not ask
for is not a faster answer, it is a change to something real that nobody reviewed.

## The rules

- **`snake_case` for every resource, variable, output and local**, and descriptive over short — the name is
  read in a plan diff months later, by someone who does not have the file open.
- **Providers are pinned with `~>` in `required_providers`**, and `required_version` is set. An unpinned
  provider makes a plan a function of when it ran.
- **The module layout is flat.** A `modules/` directory is for reuse that exists, not reuse that is
  anticipated; a module with one caller is a directory boundary bought with two files of plumbing.
- **Variables carry a `type` and a `description`**, and a `default` only where the value is genuinely
  optional. A variable that must be set has no default, so a missing value fails at plan rather than
  applying something plausible.
- **`terraform validate` after any structural change** — a moved block or a renamed module reference is the
  class of mistake it catches for free.

## Before finishing

`.editorconfig` wins over anything here. Run the repo's own lint entry point over what changed rather than
`terraform fmt` directly, and resolve every finding before reporting the work done.
