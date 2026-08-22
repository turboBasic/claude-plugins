# scaffold

Execute `generate.py` with the project directory and a context JSON file as arguments:

```sh
mise exec -- python milestones/01-scaffold/generate.py <project_dir> <context_json_path>
```

The context JSON must contain:

```json
{
  "project_name": "<project_name>",
  "package_name": "<package_name>",
  "description": "<description>"
}
```

`<project_dir>` is the absolute or relative path to the target project directory (created if absent).
`<context_json_path>` is the path to a JSON file with the three keys above.

On success the script prints a JSON object `{"status": "done", "milestone": "01-scaffold", "notes": [...]}` to stdout and exits 0.
