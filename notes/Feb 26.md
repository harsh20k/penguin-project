5## Feb 26 – Factor 3 redesign + DynamoDB migration + live backend test

### Changes made

#### Factor 3 – user-provided rotation key
- Rotation key is now **set by the user at signup** (integer 1–25), not randomly assigned.
- `SignupRequest` model (`app/models/session.py`) validates `rotation` is 1–25 via a Pydantic `field_validator`.
- The key is stored in DynamoDB `user_mfa` table alongside the security Q&A (already the case; now enforced at the model level).
- **The challenge response no longer returns `rotation`** — `Factor3ChallengeResponse` only contains `plaintext`. The user is expected to know their own key.
- Plaintext challenge length reduced from **8 → 4 characters** so it's easier to solve manually.

#### Factor 3 – DynamoDB-backed challenges
- Previously, `caesar_challenges` were stored in SQLite on Lambda `/tmp`. This broke in AWS because challenge and verify requests can hit different Lambda instances (different `/tmp` filesystems).
- `app/services/factor3_service.py` rewritten to use a new **`challenges` DynamoDB table** when `CHALLENGES_TABLE_NAME` env var is set (i.e. in AWS). Falls back to SQLite for local dev.
- Challenges have a **10-minute TTL** (auto-deleted by DynamoDB).
- Race condition handled: if two Lambda instances try to create the same challenge simultaneously, the second write is ignored and the first challenge is returned.

#### Terraform
- New DynamoDB table `penguin-auth-challenges-<env>` (hash key: `session_id`, TTL on `ttl`).
- IAM policy updated to grant Lambda `GetItem`, `PutItem`, `DeleteItem` on the challenges table.
- `CHALLENGES_TABLE_NAME` added to all Lambda env vars.

#### Handlers cleaned up
- `handlers/factor3_challenge.py` and `handlers/factor3_verify.py` — removed `init_db()` calls (SQLite setup no longer needed for factor 3 in Lambda).

---

### Live backend test (AWS)

API: `https://odwyc10krd.execute-api.us-east-1.amazonaws.com` (redeployed; previous URL was `6fov0pmqkk`)

| Step | Result |
|---|---|
| `GET /` | 200 – `{"service": "Penguin Auth API"}` |
| `POST /auth/signup` | 200 – `{"user_id": "24f884d8-e041-70aa-2c4a-a07ea5da665b"}` |
| `POST /auth/login` | 200 – session + token returned |
| `GET /auth/factor2/question` | 200 – `{"question": "What is your favorite color?"}` |
| `POST /auth/factor2/verify` | 200 – `{"success": true}` |
| `GET /auth/factor3/challenge` | 200 – plaintext returned (factor 3 challenge was still SQLite-backed at time of test; 403 on verify due to Lambda instance mismatch — fixed by DynamoDB migration above) |

**Known issue resolved:** Factor 3 verify returned 403 even with the correct ciphertext because the challenge was stored in `/tmp` SQLite on one Lambda container and the verify call hit a different container. Fixed by moving challenges to DynamoDB.

---

### Frontend "Load failed" bug fix

**Root cause:** Two issues found via runtime debug logs:
1. `frontend/.env` had a trailing `/` in `VITE_API_BASE` (e.g. `https://odwyc10krd.../`), causing a double-slash URL (`//auth/signup`) that API Gateway rejected.
2. API Gateway had no `cors_configuration`, so the browser's `OPTIONS` CORS preflight for `POST /auth/signup` was blocked, resulting in `TypeError: Load failed` before any HTTP response was received.

**Fixes:**
- `frontend/.env` — removed trailing slash from `VITE_API_BASE`.
- `frontend/src/api/client.ts` — added `.replace(/\/$/, '')` to defensively strip trailing slashes from the base URL.
- `terraform/api_gateway.tf` — added `cors_configuration` block to `aws_apigatewayv2_api` allowing `GET`, `POST`, `OPTIONS` from all origins with `content-type` and `authorization` headers.

---

### Deploy steps (after these changes)

```bash
# 1. Rebuild zip from repo root
./terraform/scripts/build_lambda.sh

# 2. Apply Terraform (creates challenges table, CORS config, updates IAM + env vars)
cd terraform && terraform apply
```

See `notes/awsDeploy.md` for full deploy and test instructions.
