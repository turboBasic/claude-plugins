---
name: shell
description: Lay a shell script out top-down - a header, strict mode, main() before every helper, and the invocation on the last line. Use when writing or modifying a .sh or .bash file, or when reviewing generated shell before it reaches disk.
---

# Shell script structure

Applies to every `.sh` and `.bash` file written or touched. A script that does not match this shape yet is
refactored into it as part of the change that touches it.

## The order

1. **Shebang** — `#!/usr/bin/env bash`.
2. **Header comment** — one-line purpose, usage, options, one example.
3. **Strict mode** — `set -euo pipefail`, plus `IFS=$'\n\t'` where word-splitting matters.
4. **`main()`** — declared before every other function.
5. **Helpers** — one per step named in `main()`, below it, in roughly call order.
6. **Invocation** — `main "$@"` as the last line.

`main()` sets what it must and calls helpers; each line reads as one high-level step. No business logic in
it, no nested loops, no `case` beyond argument parsing. Helpers take verb names — `validate_inputs`,
`run_destroy` — declare every variable `local`, and let `set -e` propagate failure rather than swallowing
it. Nothing runs at the top level but `set …`, the constants `main()` genuinely cannot own, and `main "$@"`.

**`.editorconfig` wins over anything below.** Read it before writing, for indentation, line endings,
charset and final newline.

## Template

```bash
#!/usr/bin/env bash
#
# <one-line purpose>
#
# Usage:
#   ./script-name.sh [--flag VALUE] [ARG]
#
# Options:
#   --flag VALUE   <description>
#
# Example:
#   ./script-name.sh --flag foo bar
#

set -euo pipefail

main() {
  REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
  TARGET="${1:-default}"

  parse_args "$@"
  validate_inputs
  do_the_thing
  cleanup
}

parse_args() { :; }

validate_inputs() {
  local dir="$REPO_ROOT/$TARGET"
  [[ -d "$dir" ]] || { echo "ERROR: missing $dir" >&2; exit 1; }
}

do_the_thing() { :; }

cleanup() { :; }

main "$@"
```

## Before finishing

Run the repo's hook runner over the file it changed — the `lint` entry point where one exists, otherwise
the hook runner directly against that path. Resolve every finding before reporting the task done.
