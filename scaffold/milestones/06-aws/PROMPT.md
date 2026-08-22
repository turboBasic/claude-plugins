# aws

Add a boto3 S3 client wrapper with typed responses, structured logging, and AWS profile support.

Context keys: `package_name`, `flags`

`flags` contains `["--aws"]` when the `--aws` flag was set. The AWS service is always `s3`.

## Constraints

- Never hardcode credentials — use boto3 credential chain (profile, env vars, instance role).

## Steps

1. **command** — `mise exec -- uv add boto3`
   Adds boto3 as a runtime dependency.

2. **command** — `mise exec -- uv add --group lint "boto3-stubs[s3]"`
   Adds typed stubs for s3 to the lint group only.

3. **file** — `src/<package_name>/aws/__init__.py` (empty)

4. **file** — `src/<package_name>/aws/models.py`
   Pydantic `BaseModel` subclasses for AWS response types.
   Keep models minimal — wrap the key fields returned by the primary S3 operation.

5. **file** — `src/<package_name>/aws/s3.py`
   Requirements:
   - Typed `get_client` factory — never hardcoded credentials.
   - Region from `config.aws_region` — add `aws_region: str` to `AppConfig` in `config.py`
     if not already present.
   - At least one operation function that uses the typed client and returns a Pydantic model.
   - Use `structlog` for logging with relevant context fields bound.
   - `AppConfig` injected as argument — never imported from bootstrap or environment directly.

## Notes

Each bullet below becomes one string in the `notes` array (3 entries expected):

- AWS service(s) configured and the primary operation implemented
- Pydantic response model name(s) and key fields wrapped
- How region is resolved (config field name added to `AppConfig`)
