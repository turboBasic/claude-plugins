---
name: go
description: Hold a Go project to one shape - a module per deployable unit, errors returned and wrapped, dependencies passed rather than global, table-driven tests. Use when writing or modifying a .go file, when laying out a Go module, or when reviewing generated Go before it reaches disk.
---

# Go project shape

Applies to every `.go` file written or touched, and to the module layout around it.

## Layout

**One `go.mod` per deployable unit or library.** A repository holding several is several modules, not one
module with several `main` packages — the version a consumer imports is the module's, so a library sharing a
`go.mod` with a binary ships the binary's dependency graph.

## The rules

- **Return errors; do not panic.** A `panic` is for a violated invariant the caller cannot act on, not for a
  failure the caller can handle. Wrap with `fmt.Errorf("doing the thing: %w", err)` so `errors.Is` and
  `errors.As` still reach the cause, and give the wrapping message the operation rather than the error.
- **No global state.** Dependencies arrive through a constructor or a function parameter. A package-level
  variable that is written after `init` is state two tests share, which is why the second one fails only
  when the suite runs in order.
- **Tests are table-driven** where a behaviour has cases: a slice of named cases, one `t.Run` per row,
  `t.Parallel()` where the case allows it. `go test ./...` is the whole command.
- **`gofmt` and `goimports` own the formatting**, and there is no custom style to argue about. `golangci-lint`
  reads the project's `.golangci.yml`; a rule that has to go is turned off there with a comment giving the
  reason, never with a bare `//nolint`.
- **Exported identifiers carry doc comments; unexported ones carry none unless the why is non-obvious.**
  A comment restating the signature is noise the compiler already checks.

## Before finishing

`.editorconfig` wins over anything here — indentation, line endings, charset, final newline. Read it before
writing.

Run the repo's own lint entry point over what changed rather than `gofmt` or `golangci-lint` directly, and
resolve every finding before reporting the work done.
