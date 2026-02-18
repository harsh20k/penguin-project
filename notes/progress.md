# Progress (Module 1 scope)

**Scope:** User Management & Authentication — sign-up validation + 3FA (Cognito, Q&A, Caesar cipher).

**Last updated:** 2026-02-18

---

## Current state

- **Docs:** Implementation plan in `notes/plan.md`; AWS deploy instructions in `notes/awsDeploy.md`.
- **Local backend (done):** FastAPI under `backend/`:
  - SQLite: users, sessions, security_qa, caesar_config, caesar_challenges.
  - `POST /auth/login` → session + token; factor 2 (Q&A) and factor 3 (Caesar) endpoints; FSM via dependencies.
  - Seed script `backend/seed_local.py` (dev user: dev@local / devpass, Q: favorite color / A: blue, rotation 7).
- **Front-end (done for local & AWS):** React app in `frontend/` — 3-step MFA flow wired via `frontend/src/api/client.ts`, with optional **Sign up** button on login step.
- **AWS infra (partially deployed):**
  - Terraform config for:
    - API Gateway HTTP API + `$default` stage.
    - Lambda function (FastAPI app) + IAM execution role.
    - Cognito User Pool + SPA client (created during last apply).
    - DynamoDB `user_mfa` table definition + IAM inline policy for Lambda to read/write it.
  - Current AWS state after first `terraform apply`:
    - API Gateway and `$default` stage created.
    - Cognito User Pool and app client created.
    - Lambda role created and basic execution policy attached.
    - **DynamoDB table creation failed** once due to IAM `AccessDenied` on `dynamodb:CreateTable`; IAM requirements are now documented in `notes/awsDeploy.md` so next apply can succeed once permissions are fixed.
- **Auth logic (code-level):**
  - `POST /auth/signup` and `POST /auth/login` now use **Cognito + DynamoDB** via `app/aws_integration.py`.
  - Factor 2 and factor 3 services read MFA config from DynamoDB, but factor 3 still uses SQLite in Lambda for per-session challenges.

---

## Remaining steps

1. **Fix IAM + complete Terraform deploy**
   - Grant required IAM permissions for `dynamodb:CreateTable` etc. per `notes/awsDeploy.md`.
   - Re-run `terraform apply` until DynamoDB `penguin-auth-users-<env>` table and Lambda env vars are created successfully.
2. **Wire signup body correctly**
   - Update `/auth/signup` in `backend/app/routers/auth_router.py` to accept a JSON body (Pydantic model) matching `frontend/src/api/client.ts` so `Sign up` works end-to-end against Cognito + DynamoDB.
3. **End-to-end AWS MFA test**
   - Point frontend at `VITE_API_BASE=<api_url>` from Terraform.
   - Create a new Cognito-backed user via **Sign up**, then run through factor 2 and factor 3 in the browser.
   - Capture required screenshots (frontend + AWS console: Cognito user + DynamoDB row).
4. **Hardening & tests**
   - Add unit/integration tests for Cognito/DynamoDB-backed auth.
   - Consider session expiry, basic rate limiting, and clearer error messages for failed factors.
