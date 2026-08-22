<!-- pyml disable MD041 -->

<!-- These rules are inserted after every PROMPT.md -->

## Before outputting the result, verify

- Every file written or modified resolves within `project_dir` — no paths outside it were touched.
- The `notes` array contains one string per item listed in the milestone's `## Notes` section. If the milestone lists 3 items to report, `notes` has 3 entries.
- The output line is valid JSON: parseable by `json.loads()`, no trailing commas, no single quotes, no unescaped characters, no markdown fencing around it.
