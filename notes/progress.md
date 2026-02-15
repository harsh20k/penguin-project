# Progress (Module 1 scope)

**Scope:** User Management & Authentication — sign-up validation + 3FA (Cognito, Q&A, Caesar cipher).

**Last updated:** 2026-02-14

---

## Current state

- **Docs:** Module 1 implementation steps in `notes/Module1 implementation steps.md`; plan in `notes/plan.md`.
- **Local backend (done):** Python FastAPI app under `backend/`:
  - SQLite tables: users, sessions, security_qa, caesar_config, caesar_challenges.
  - Dev login stub: `POST /auth/login` (username/password) → session + token.
  - Factor 2: `GET /auth/factor2/question`, `POST /auth/factor2/verify` (hashed Q&A, constant-time).
  - Factor 3: `GET /auth/factor3/challenge`, `POST /auth/factor3/verify` (Caesar encode, constant-time compare).
  - FSM enforced via dependencies (require_factor1, require_factor2).
  - Seed script `backend/seed_local.py` + README with run instructions.
- **Not yet:** AWS resources, Lambdas, front-end, or sign-up persistence in the local app.

---

## Remaining steps

1. **Run and test local API** — `pip install -r requirements.txt`, `python seed_local.py`, `uvicorn app.main:app --reload`; exercise full flow (login → factor2 → factor3) e.g. via curl or script.
2. **Front-end** — React (or similar) app: login screen calling `/auth/login`, then 3-step flow (Q&A step, Caesar step); optional sign-up UI and post–sign-up Q&A + Caesar setup.
3. **AWS & data** — DynamoDB tables and Cognito User Pool; Lambdas for session, factor-2, factor-3; API Gateway; migrate logic from FastAPI or keep FastAPI as local-only.
4. **Hardening & tests** — Hashed Q&A and constant-time compare (done locally); add HTTPS, rate limiting, TTL; unit/integration tests for Lambdas and full 3FA.
