# Penguin Auth API

FastAPI backend that implements a 3-step MFA flow:

1. Username/password (factor 1)
2. Security question/answer (factor 2)
3. Caesar cipher challenge (factor 3)

It supports two modes:

- **Local dev mode** – uses SQLite only (no AWS).
- **Deployed mode (via Lambda)** – uses **AWS Cognito + DynamoDB** for user auth and MFA metadata.

## Setup (local dev)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Seed dev user (SQLite only)

Creates one user with a security question and Caesar config so the full 3-step login works locally:

```bash
python seed_local.py
```

Default local credentials:

- **Email:** `dev@local`
- **Password:** `devpass`
- **Security answer:** `blue` (question: "What is your favorite color?")
- **Caesar:** encode the challenge plaintext with rotation **7**

### Run FastAPI locally

```bash
uvicorn app.main:app --reload
```

API base: `http://127.0.0.1:8000`. Docs: `http://127.0.0.1:8000/docs`.

### Auth flow (local)

1. **POST /auth/login** – body `{"username": "dev@local", "password": "devpass"}` → returns `session_id` and `token`.
2. **GET /auth/factor2/question** – header `Authorization: Bearer <token>` → returns security question.
3. **POST /auth/factor2/verify** – body `{"answer": "blue"}` → marks factor 2 done.
4. **GET /auth/factor3/challenge** – returns `plaintext` and `rotation`; encode plaintext with Caesar (shift by `rotation`) to get the expected ciphertext.
5. **POST /auth/factor3/verify** – body `{"ciphertext": "<encoded string>"}` → returns `{"authenticated": true}`.

## Deployed mode (Cognito + DynamoDB)

When deployed via the Terraform in `terraform/`, the same FastAPI app is packaged as a Lambda behind API Gateway.

- **Factor 1 (signup/login)** uses **AWS Cognito User Pool** via:
  - `POST /auth/signup` – creates a Cognito user and stores MFA metadata in DynamoDB.
  - `POST /auth/login` – authenticates via Cognito and starts a local session (returns `session_id`, `token`, and Cognito tokens).
- **Factor 2 (security question)** uses DynamoDB-stored Q&A.
- **Factor 3 (Caesar)** uses rotation from DynamoDB and stores challenges in SQLite inside the Lambda (`/tmp/local.db`), which is fine for short-lived sessions.

### Important environment variables (Lambda)

- `COGNITO_USER_POOL_ID` – Cognito User Pool ID.
- `COGNITO_CLIENT_ID` – Cognito app client ID.
- `DDB_USER_TABLE_NAME` – DynamoDB table name for MFA metadata.
- `DB_PATH` – SQLite file path for session/challenges (default `/tmp/local.db` in Lambda).

## Testing checklist

- Run the React frontend against the deployed API Gateway URL:
  - Sign up a new user via the **Sign up** button on the login step.
  - Log in with that user and complete factor 2 and factor 3.
- Verify in AWS:
  - User appears in the Cognito User Pool.
  - MFA metadata (question, answer hash, rotation) appears in the DynamoDB user table.
- Capture screenshots of:
  - Successful signup and login.
  - Factor 2 and factor 3 screens.
  - AWS console views for Cognito and DynamoDB.
