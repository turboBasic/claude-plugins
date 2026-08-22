# tests

Add pytest unit and integration tests with coverage enforcement; verify the full test suite passes.

Context keys: `package_name`, `flags`

`flags` determines which optional integrations to set up:

- `--aws` present → add `moto` mocking in integration tests
- http milestone always runs, so always add `respx` mocking

## Constraints

- Do not mock `configure_logging` — it must be exercised on every CLI invocation.
- Integration tests must use `respx` for HTTP mocking, not real network calls.

## Steps

1. **command** — `mise exec -- uv add --group test pytest-asyncio respx`
   Always added — http milestone is always present.

2. **command** — `mise exec -- uv add --group test moto`
   Only if `--aws` is in `flags`.

3. **file** — `tests/unit/__init__.py` (empty)

4. **file** — `tests/unit/test_config.py`
   One unit test: instantiate `AppConfig` with default values and assert the default `log_level`.
   No AWS or HTTP calls.

5. **file** — `tests/unit/test_cli.py`
   Use `typer.testing.CliRunner` to invoke the app's `app` object.
   Assert the exit code is 0 and the output is non-empty.
   This exercises `configure_logging` on every run — do not mock it out.

6. **file** — `tests/integration/__init__.py` (empty)

7. **file** — `tests/integration/conftest.py`
   Fixtures for integration tests.
   - Always: `app_config` fixture returning a test `AppConfig` instance.
   - If `--aws`: fixtures for dummy AWS credentials and a moto-mocked service client.

8. **file** — `tests/integration/test_http.py`
   One integration test using `respx` to mock an HTTP call via `get_client`.
   Assert the client returns a parsed response model (or raises on 5xx).

9. **file** — `tests/integration/test_cli.py`
   Use `respx` to mock the upstream API endpoint and `typer.testing.CliRunner` to invoke the app.
   Assert exit code is 0 and each astronaut name from the mocked response appears in the output.

10. **file** — update `pyproject.toml`
   Add `[tool.coverage.run]` and `[tool.coverage.report]` with `fail_under = 80`.

11. **file** — update `justfile`
    Add recipes:
    - `test-unit`: `mise exec -- pytest tests/unit`
    - `test-integration`: `mise exec -- pytest tests/integration`
    - `test-cov`: `mise exec -- pytest --cov --cov-report=term-missing`

## Notes

Each bullet below becomes one string in the `notes` array (3 entries expected):

- Test count and coverage percentage achieved
- Whether moto was added (only when `--aws` in `flags`)
- Any async test marker used (`@pytest.mark.asyncio` vs `asyncio_mode=auto`)
