# Penguin Auth – 3FA Architecture

## Overview

Penguin Auth is a three-factor authentication system deployed on AWS. It uses Cognito for password-based authentication (factor 1), a security question/answer stored in DynamoDB (factor 2), and a Caesar cipher challenge using a user-chosen rotation key (factor 3). All backend logic runs as seven independent Lambda functions behind API Gateway HTTP API v2.

---

## AWS Infrastructure

```
Client (SPA)
    │
    ▼
API Gateway HTTP API v2
    │
    ├── GET  /                    → Lambda: root
    ├── POST /auth/signup         → Lambda: signup
    ├── POST /auth/login          → Lambda: login
    ├── GET  /auth/factor2/question  → Lambda: factor2_question
    ├── POST /auth/factor2/verify    → Lambda: factor2_verify
    ├── GET  /auth/factor3/challenge → Lambda: factor3_challenge
    └── POST /auth/factor3/verify   → Lambda: factor3_verify
```

All seven Lambdas share the same deployment zip (`penguin-api.zip`) but each points to a different handler (`handlers.<name>.handler`). They share the same IAM role and environment variables.

### DynamoDB Tables

| Table | Hash Key | Purpose |
|---|---|---|
| `penguin-auth-users-<env>` | `user_id` | MFA config: role, security Q&A hash, Caesar rotation key |
| `penguin-auth-tokens-<env>` | `token` | Session tokens (24h TTL) |
| `penguin-auth-sessions-<env>` | `session_id` | Session state: factor1/2/3 completion flags |
| `penguin-auth-challenges-<env>` | `session_id` | Active Caesar challenges (10-min TTL) |

### Cognito

- User Pool: email-based login, email auto-verified, password min 8 chars.
- User Pool Client: `ALLOW_USER_PASSWORD_AUTH`, `ALLOW_USER_SRP_AUTH`, `ALLOW_REFRESH_TOKEN_AUTH`. No OAuth flows.

---

## Signup Flow

```
Client                          Lambda: signup              Cognito         DynamoDB (users)
  │                                    │                       │                  │
  │── POST /auth/signup ──────────────▶│                       │                  │
  │   {email, password,                │                       │                  │
  │    question, answer,               │── AdminCreateUser ───▶│                  │
  │    rotation (1–25)}                │── AdminSetUserPassword▶│                  │
  │                                    │── AdminGetUser ───────▶│                  │
  │                                    │   (get Cognito sub)    │                  │
  │                                    │                        │                  │
  │                                    │── PutItem ────────────────────────────────▶
  │                                    │   {user_id (sub), email, role,            │
  │                                    │    question, answer_hash, rotation}        │
  │◀── {user_id} ─────────────────────│                                            │
```

**Key points:**
- `answer` is hashed with `sha256_crypt` (passlib) before storage. The plaintext answer is never stored.
- `rotation` is validated to be 1–25. This is the user's personal Caesar cipher key.
- `user_id` is the Cognito sub (UUID), used as the primary key across all DynamoDB tables.

---

## Login Flow (3 Factors)

### Factor 1 – Password (Cognito)

```
Client                      Lambda: login               Cognito         DynamoDB (tokens, sessions)
  │                               │                        │                      │
  │── POST /auth/login ──────────▶│                        │                      │
  │   {username, password}        │── InitiateAuth ───────▶│                      │
  │                               │◀── {AccessToken,       │                      │
  │                               │     IdToken, ...}      │                      │
  │                               │── GetUser(AccessToken)─▶│                      │
  │                               │◀── {sub (user_id)}     │                      │
  │                               │                        │                      │
  │                               │── create_session(user_id, factor1_done=True) ─▶
  │                               │── issue_token(session_id) ───────────────────▶│
  │                               │   (stored in tokens table, 24h TTL)           │
  │◀── {session_id, token,        │                                               │
  │     id_token, access_token} ──│                                               │
```

The `token` returned here is a Bearer token used for all subsequent factor 2 and factor 3 calls.

---

### Factor 2 – Security Question

**Get question:**
```
Client                      Lambda: factor2_question        DynamoDB (users, sessions, tokens)
  │                               │                                  │
  │── GET /auth/factor2/question ─▶│                                  │
  │   Authorization: Bearer <token>│── resolve_token(token) ─────────▶│
  │                                │◀── session_id                    │
  │                                │── get_session(session_id) ───────▶│
  │                                │   (checks factor1_done=1)        │
  │                                │── get_user_mfa_config(user_id) ──▶│
  │◀── {question} ─────────────────│                                  │
```

**Verify answer:**
```
Client                      Lambda: factor2_verify          DynamoDB (users, sessions)
  │                               │                                  │
  │── POST /auth/factor2/verify ──▶│                                  │
  │   {answer}                     │── verify_answer(user_id, answer) │
  │                                │   (bcrypt verify against hash)   │
  │                                │── set_factor2_done(session_id) ──▶│
  │◀── {success: true} ────────────│                                  │
```

---

### Factor 3 – Caesar Cipher Challenge

**Get challenge:**
```
Client                      Lambda: factor3_challenge    DynamoDB (users, sessions, challenges)
  │                               │                                  │
  │── GET /auth/factor3/challenge ─▶│                                  │
  │   Authorization: Bearer <token>│── require_factor2 check ─────────▶│
  │                                │── get_user_mfa_config(user_id) ──▶│
  │                                │   (fetches rotation key)         │
  │                                │── generate 4-char random plaintext│
  │                                │── compute expected =             │
  │                                │   caesar_encode(plaintext, rotation)
  │                                │── PutItem(session_id, plaintext, │
  │                                │   expected_ciphertext, ttl=10min)─▶│
  │◀── {plaintext} ────────────────│                                  │
  │   (rotation NOT returned)      │                                  │
```

The user sees a 4-character plaintext (e.g. `"aBcD"`). They apply their rotation key (the one they chose at signup) to compute the ciphertext manually.

**Verify ciphertext:**
```
Client                      Lambda: factor3_verify       DynamoDB (challenges, sessions)
  │                               │                                  │
  │── POST /auth/factor3/verify ──▶│                                  │
  │   {ciphertext}                 │── GetItem(session_id) ───────────▶│
  │                                │◀── {expected_ciphertext}         │
  │                                │── constant_time_compare(         │
  │                                │   submitted, expected)           │
  │                                │── set_factor3_done(session_id) ──▶│
  │◀── {authenticated: true} ──────│                                  │
```

`constant_time_compare` uses `secrets.compare_digest` to prevent timing attacks.

---

## Caesar Cipher

The cipher shifts each letter by `rotation` positions, wrapping within A–Z and a–z independently. Non-letter characters are passed through unchanged.

```
plaintext:  a b c d  →  (rotation=2)  →  ciphertext: c d e f
plaintext:  X Y Z    →  (rotation=2)  →  ciphertext: Z A B
```

The rotation key (1–25) is the user's secret. It is stored in DynamoDB `users` table at signup and never returned to the client after that point.

---

## Session State Machine

A session progresses through three flags stored in DynamoDB `sessions`:

```
[created]
    │
    ▼ POST /auth/login (Cognito success)
factor1_done = 1
    │
    ▼ POST /auth/factor2/verify (correct answer)
factor2_done = 1
    │
    ▼ POST /auth/factor3/verify (correct ciphertext)
factor3_done = 1  →  AUTHENTICATED
```

Each factor endpoint checks that all prior factors are complete before proceeding (`require_session`, `require_factor1`, `require_factor2` guards).

---

## Token Lifecycle

| Token | Storage | TTL | Purpose |
|---|---|---|---|
| Cognito `AccessToken` | Client only | ~1h (Cognito-managed) | Used once to resolve Cognito sub at login |
| Penguin `token` | DynamoDB `tokens` table | 24h | Bearer token for factor 2/3 API calls |
| Session | DynamoDB `sessions` table | No TTL | Tracks factor completion flags |
| Caesar challenge | DynamoDB `challenges` table | 10 min | Stores expected ciphertext per session |

---

## Local Development

For local dev, all DynamoDB tables are replaced by SQLite (`/tmp/local.db` or `backend/local.db`). The FastAPI app runs via `uvicorn app.main:app`. Token storage falls back to an in-memory dict. The same handler logic runs in both environments.

```bash
cd backend
uvicorn app.main:app --reload
python seed_local.py   # seeds a dev user (dev@local / devpass, rotation=7)
```

---

## Security Notes

- Answers to security questions are stored as `sha256_crypt` hashes (passlib). Never in plaintext.
- Caesar cipher comparison uses `secrets.compare_digest` (constant-time) to prevent timing attacks.
- The rotation key is never returned to the client after signup.
- Challenge TTL (10 min) limits the window for brute-force attempts on a captured challenge.
- Tokens have a 24-hour TTL and are stored in DynamoDB (not JWTs), so they can be invalidated server-side.
