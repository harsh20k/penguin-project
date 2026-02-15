# Penguin Auth API (local)

Module 1 auth backend: session + factor-2 (Q&A) + factor-3 (Caesar). Uses SQLite and a dev login stub instead of Cognito.

## Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

## Seed dev user

Creates one user with a security question and Caesar config so the full 3-step login works:

```bash
python seed_local.py
```

Default credentials:

- **Email:** `dev@local`
- **Password:** `devpass`
- **Security answer:** `blue` (question: "What is your favorite color?")
- **Caesar:** encode the challenge plaintext with rotation **7**

## Run

```bash
uvicorn app.main:app --reload
```

API base: `http://127.0.0.1:8000`. Docs: `http://127.0.0.1:8000/docs`.

## Auth flow (local)

1. **POST /auth/login** – body `{"username": "dev@local", "password": "devpass"}` → returns `session_id` and `token`.
2. **GET /auth/factor2/question** – header `Authorization: Bearer <token>` → returns security question.
3. **POST /auth/factor2/verify** – body `{"answer": "blue"}` → marks factor 2 done.
4. **GET /auth/factor3/challenge** – returns `plaintext` and `rotation`; encode plaintext with Caesar (shift by `rotation`) to get the expected ciphertext.
5. **POST /auth/factor3/verify** – body `{"ciphertext": "<encoded string>"}` → returns `{"authenticated": true}`.

## Env

- `DB_PATH` – SQLite file path (default: `backend/local.db`).
- `DEV_MODE` – unused currently; reserved for toggling stub vs Cognito.
