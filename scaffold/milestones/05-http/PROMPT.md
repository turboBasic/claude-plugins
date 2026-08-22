# http

Async-first HTTP client layer using httpx with tenacity retry logic, structured logging, and a Pydantic response model.

Context keys: `package_name`

## Constraints

- Never retry 4xx — call `response.raise_for_status()` outside the retried path.
- Never use `requests` or `aiohttp` — use `httpx.AsyncClient` only.

## Steps

1. **command** — `mise exec -- uv add httpx tenacity`
   Adds runtime dependencies to `pyproject.toml` and updates `uv.lock`.

2. **file** — `src/<package_name>/http/__init__.py` (empty)

3. **file** — `src/<package_name>/http/models.py`
   Pydantic `BaseModel` subclasses for HTTP request/response types.
   Include at minimum a generic error response model.

4. **file** — `src/<package_name>/http/client.py`
   Requirements:
   - Use `httpx.AsyncClient` — never `requests` or `aiohttp`
   - Expose the client via `@asynccontextmanager` returning an `AsyncClient`
   - Set explicit `httpx.Timeout`
   - Use `tenacity` for retries on transient failures (5xx, network errors);
     include a `_retryable` predicate function
   - Never retry 4xx — call `response.raise_for_status()` outside the retried function
   - Use `structlog` for logging
   - `AppConfig` injected as argument — never imported from bootstrap or environment directly
   - Provide a `async def fetch(config: AppConfig) -> <ResponseModel>` function that opens
     the client, performs the request(s) the project requires, and returns a parsed response model.
     This is the single callable surface the CLI uses.

5. **file** — update `src/<package_name>/cli.py`
   Replace the placeholder body of `main()` with real logic using the `fetch` function:
   - Call `asyncio.run(fetch(config))` to bridge the sync Typer command into the async HTTP layer.
   - Print the results to stdout using `rich.console.Console`.
   Typer commands are synchronous — `asyncio.run()` is the correct bridge, not `async def main`.

## Notes

Each bullet below becomes one string in the `notes` array (3 entries expected):

- The base URL(s) used by the HTTP client
- The Pydantic response model(s) defined and their key fields
- Tenacity retry configuration chosen (attempts, wait strategy, retried status codes)
