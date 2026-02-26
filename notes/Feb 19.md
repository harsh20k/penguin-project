## Feb 19 – Per-route Lambdas (no Mangum)

The deployed backend uses **seven Lambda functions** instead of a single Mangum-wrapped FastAPI Lambda. Each route has its own handler; Mangum is not used in the Lambda runtime.

### What’s in place

- **`backend/app/lambda_utils.py`** – Shared helpers for API Gateway HTTP API v2: event parsing (`get_body_json`, `get_auth_token`), response builders with CORS (`json_response`, `error_response`), and `require_session(event, require_factor1=..., require_factor2=...)` for token and factor checks.
- **`backend/handlers/`** – One module per route: `root`, `signup`, `login`, `factor2_question`, `factor2_verify`, `factor3_challenge`, `factor3_verify`. Each exposes `handler(event, context)` and calls existing `app.*` logic.
- **Terraform** – Seven `aws_lambda_function` resources (same zip, same env, different handler), seven API Gateway integrations and routes. No catch-all proxy. Seven `aws_lambda_permission` resources. Outputs reference the root Lambda.
- **Build** – `terraform/scripts/build_lambda.sh` copies `app/` and `handlers/` into the zip (no `lambda_handler.py`). Handlers are `handlers.root.handler`, `handlers.signup.handler`, etc.
- **Dependencies** – Mangum removed from `backend/requirements.txt`. Local dev unchanged: `uvicorn app.main:app` still runs the FastAPI app.

### Git: don’t commit `.terraform/`

Run `terraform init` only locally. The `.terraform/` directory (including large provider binaries) is in `.gitignore`. Do not commit it—GitHub rejects files over 100 MB. If you already committed it, remove from the index with `git rm -r --cached terraform/.terraform` and fix history if needed (e.g. `git filter-repo` or BFG).
