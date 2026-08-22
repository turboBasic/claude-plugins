# config

Add Dynaconf + Pydantic v2 configuration layer with environment-aware settings and typed AppConfig.

Context keys: `project_name`, `package_name`

## Constraints

- Only `bootstrap.py` imports dynaconf. All other modules depend only on `AppConfig` from `config.py`.
- `load_raw_config()` must return **lowercase** keys. Dynaconf normalises keys to uppercase internally; Pydantic silently ignores uppercase keys and falls back to defaults.

## Packages

| Package | Role |
| --- | --- |
| `dynaconf` | raw config loading; **bootstrap.py only** |
| `pydantic` | config schema and validation |
| `platformdirs` | XDG-compliant config file path |

The config layer uses a hard boundary: Dynaconf loads raw values, Pydantic v2 validates them.
Only `bootstrap.py` may import dynaconf. All application code depends only on `AppConfig`.

## Steps

1. **command** — `mise exec -- uv add dynaconf pydantic platformdirs`
   Adds runtime dependencies to `pyproject.toml` and updates `uv.lock`.

2. **file** — `src/<package_name>/config.py`
   Uses `pydantic` — must not import `dynaconf` or `platformdirs`.
   Write this file with exactly this structure:

   ```python
   from pydantic import BaseModel, Field


   class AppConfig(BaseModel):
       log_level: str = Field(default="INFO")


   def load_config() -> "AppConfig":
       from <package_name>.bootstrap import load_raw_config

       return AppConfig(**load_raw_config())
   ```

3. **file** — `src/<package_name>/bootstrap.py`
   The ONLY file that imports dynaconf. Write this file with exactly this structure:

   ```python
   from typing import Any

   import platformdirs
   from dynaconf import Dynaconf


   def load_raw_config() -> dict[str, Any]:
       config_dir = platformdirs.user_config_dir("<project_name>")
       config_file = f"{config_dir}/config.yaml"

       settings = Dynaconf(
           envvar_prefix="<PACKAGE_NAME_UPPER>",
           settings_files=[config_file],
       )

       return {k.lower(): v for k, v in settings.to_dict().items()}
   ```

   Replace `<project_name>` with the actual project name string literal.
   Replace `<PACKAGE_NAME_UPPER>` with the package name in UPPER_CASE.

4. **file** — `config.example.yaml`
   At project root. First line must be a comment pointing to the XDG install path.
   Documents every key in `AppConfig` with example values and comments.
   Example:

   ```yaml
   # Copy to ~/.config/<project_name>/config.yaml to apply settings
   # Logging level: DEBUG, INFO, WARNING, ERROR
   log_level: INFO
   ```

5. **file** — update `src/<package_name>/cli.py`
   Call `load_config()` and store the result as an `AppConfig` instance.
   Pass the config to `configure_logging`.
   Both `AppConfig` and `load_config` must be referenced in `cli.py` — the verify script checks for them.

## Notes

Each bullet below becomes one string in the `notes` array (3 entries expected):

- All `AppConfig` fields added (name and type)
- The environment variable prefix used for Dynaconf (e.g. `MYAPP_`)
- The config file path template (e.g. `~/.config/<project_name>/config.yaml`)
