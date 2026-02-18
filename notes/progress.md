# Progress (Module 1 scope)

**Scope:** User Management & Authentication — sign-up validation + 3FA (Cognito, Q&A, Caesar cipher).

**Last updated:** 2026-02-17

---

## Current state

- **Docs:** Module 1 implementation steps in `notes/Module1 implementation steps.md`; plan in `notes/plan.md`.
- **Local backend (done):** FastAPI under `backend/`:
  - SQLite: users, sessions, security_qa, caesar_config, caesar_challenges.
  - `POST /auth/login` → session + token; factor 2 (Q&A) and factor 3 (Caesar) endpoints; FSM via dependencies.
  - Seed script `backend/seed_local.py` (dev user: dev@local / devpass, Q: favorite color / A: blue, rotation 7).
- **Front-end (done for local):** React app in `frontend/` — login → factor2 (Q&A) → factor3 (Caesar) → “Authenticated”; uses backend `/auth/*` via api client.
- **Infra:** `terraform/` present; `dist/` present (likely build artifacts).
- **Not yet:** AWS (Cognito, DynamoDB, Lambdas, API Gateway), sign-up flow in app, or production deploy.

---

## Remaining steps

1. **Run and test local E2E** — `pip install -r requirements.txt`, `python seed_local.py`, `uvicorn app.main:app --reload`; run frontend; complete login → factor2 → factor3 in browser.
2. **AWS auth** — DynamoDB tables + Cognito User Pool; Lambdas for session, factor-2, factor-3; API Gateway; migrate or mirror FastAPI logic.
3. **Front-end sign-up** — Sign-up UI; post–sign-up security Q&A and Caesar config (call API or Lambdas).
4. **Hardening & tests** — HTTPS, rate limiting, TTL on session/challenge; unit/integration tests for Lambdas and full 3FA.
