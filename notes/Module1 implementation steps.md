# Module 1: User Management & Authentication

Implementation steps for sign-up validation and three-factor authentication (3FA) using a lightweight front-end and backend services (AWS Cognito, DynamoDB, Lambda).

---

## Overview

| Factor | Mechanism          | Handled By            |
| ------ | ------------------ | --------------------- |
| 1st    | User ID / Password | AWS Cognito           |
| 2nd    | Question / Answer  | DynamoDB + AWS Lambda |
| 3rd    | Caesar cipher      | AWS Lambda + DynamoDB |
|        |                    |                       |

User details are stored in **DynamoDB** (or equivalent NoSQL). Authentication is **stateful** and **strictly sequential**: each factor is only attempted after the previous one has succeeded (server-side FSM).

---

## Major Implementation Steps

### 1. Environment & Prerequisites

- **AWS account** with permissions for Cognito, DynamoDB, Lambda, API Gateway (or equivalent API layer).
- **Front-end stack**: e.g. React/Vue/Svelte or static HTML+JS; ability to call REST/HTTP APIs and store tokens securely (e.g. memory or httpOnly cookies).
- **Backend entry point**: API Gateway (REST or HTTP API) or Application Load Balancer to route requests to Lambda.

---

### 2. DynamoDB Data Model

- **Tables (or single-table design)**:
  - **User profiles**: `userId` (PK), attributes (email, display name, etc.), optional link to Cognito `sub`.
  - **Security Q&A (2nd factor)**: e.g. `userId` (PK), `questionId` (SK), `question`, `answerHash` (store hashed answers, never plaintext).
  - **Caesar cipher config (3rd factor)**: e.g. `userId` (PK), `sessionId` or `configId` (SK), `rotation`, `challengePlaintext`, `expectedCiphertext` or derived validation data; consider short TTL for challenge data.

- Define **GSIs** for access patterns (e.g. lookup by Cognito `sub`, by session).
- **IAM**: Lambda execution roles with least-privilege access to these tables.

---

### 3. AWS Cognito (1st Factor)

- **User Pool**:
  - Create pool with required attributes (e.g. email, preferred_username).
  - Configure **password policy** (length, complexity).
  - Enable **sign-up** and set **sign-up validation** (e.g. required attributes, optional custom validation via Lambda triggers).
- **Sign-up flow**:
  - Front-end calls Cognito `SignUp` (or Hosted UI); validate input (format, strength) before submit.
  - Optional: **Pre sign-up / Post confirmation Lambda triggers** to sync user into DynamoDB (profile + placeholders for 2nd/3rd factor data).
- **Sign-in (1st factor)**:
  - Front-end calls Cognito `InitiateAuth` (USER_PASSWORD_AUTH) or Hosted UI.
  - On success: receive **ID / Access / Refresh tokens**; persist only what’s needed (e.g. in memory or secure cookie) and pass tokens to backend for subsequent steps.
- **Token handling**: Validate tokens in Lambda (e.g. JWT verification using Cognito JWKS) for all factor-2 and factor-3 API calls.

---

### 4. Sign-Up Validation (End-to-End)

- **Client-side**: Validate email format, password strength, required fields before calling Cognito sign-up.
- **Cognito**: Standard attribute validation + optional triggers.
- **Post sign-up (backend)**:
  - On first successful login (or post-confirmation trigger), ensure **DynamoDB profile** exists.
  - **2nd factor setup**: API (Lambda) to save hashed security Q&A for the user (after verifying Cognito token).
  - **3rd factor setup**: API to store Caesar cipher configuration (e.g. default rotation, or generate/store challenge material) per user in DynamoDB.
- Enforce **one-time setup** for 2nd and 3rd factor data so they are ready before first 3FA login.

---

### 5. Session / State (FSM) for 3FA

- **State store**: Use DynamoDB (e.g. session table or items in user table) to record completion of each factor for a given session.
  - Example: `sessionId` (PK), `userId`, `factor1Done`, `factor2Done`, `factor3Done`, `ttl`, `createdAt`.
- **Rules**:
  - Factor 2 API is only allowed if `factor1Done` is true for that session (and token valid).
  - Factor 3 API is only allowed if `factor2Done` is true.
  - After factor 3 success, set `factor3Done` and issue final session/access (e.g. custom token or flag for “fully authenticated”).
- **Session creation**: Create session record after successful Cognito sign-in (1st factor); return `sessionId` to client for subsequent requests.

---

### 6. Second Factor: Question / Answer (DynamoDB + Lambda)

- **Setup (post sign-up)**:
  - User selects questions and provides answers; front-end sends to backend.
  - Lambda hashes answers (e.g. SHA-256 or bcrypt) and stores question + hash in DynamoDB; never store plaintext answers.
- **At login**:
  - After 1st factor success, front-end requests “security question” for current session (Lambda reads from DynamoDB by `userId`/session).
  - Lambda returns one (or more) questions (no answers).
  - User submits answer(s); front-end sends to Lambda.
  - Lambda fetches stored hash(es), compares (constant-time compare); on success updates session state (`factor2Done`), returns success.
  - On failure: return generic error; optionally track attempts and lock/backoff per policy.

---

### 7. Third Factor: Caesar Cipher (Lambda + DynamoDB)

- **Concept**: User proves knowledge of a cipher procedure (e.g. “shift by N”) by solving a challenge.
- **Storage (DynamoDB)**:
  - Per user/session: store `rotation`, and either precomputed `(plaintext, ciphertext)` pair or algorithm to verify (e.g. Lambda applies rotation to user input and compares to stored expected value).
- **Challenge generation (Lambda)**:
  - For each 3rd-factor attempt, generate or retrieve a challenge (e.g. random plaintext + rotation, compute expected ciphertext, store in DynamoDB with short TTL).
  - Return to client: `plaintext` (or ciphertext to decode) and `rotation` (or instruction like “encode with rotation N”).
- **Verification (Lambda)**:
  - User submits answer (e.g. encoded/decoded string).
  - Lambda loads challenge from DynamoDB, applies same Caesar logic, compares with user answer (constant-time).
  - On success: set `factor3Done`, return final auth success; optionally issue internal token or redirect to app.
- **Caesar logic**: Implement in Lambda (e.g. Python/Node): for a given rotation R, shift A–Z (and optionally a–z) by R; use same logic for generation and verification.

---

### 8. API Design (Backend)

- **REST or HTTP API** (e.g. API Gateway + Lambda):
  - `POST /auth/session` – after Cognito login, create session, return `sessionId` (and optionally short-lived token for API calls).
  - `GET /auth/factor2/question` – return security question(s) for session (requires valid token + factor1Done).
  - `POST /auth/factor2/verify` – body: answer(s); verify, set factor2Done.
  - `GET /auth/factor3/challenge` – return Caesar challenge for session (requires factor2Done).
  - `POST /auth/factor3/verify` – body: user’s cipher answer; verify, set factor3Done, return “fully authenticated”.
- **Auth**: All these endpoints validate Cognito token (or session token) and check session state in DynamoDB before performing actions.

---

### 9. Lightweight Front-End Flow

1. **Sign-up**: Form → validate → Cognito SignUp → (optional) redirect to set security Q&A and Caesar config via backend.
2. **Login**:
   - Step 1: Username/password → Cognito → on success, call `POST /auth/session` → get `sessionId`.
   - Step 2: `GET /auth/factor2/question` → show form → `POST /auth/factor2/verify`.
   - Step 3: `GET /auth/factor3/challenge` → show cipher instruction and input → `POST /auth/factor3/verify`.
3. On full success: redirect to app or set “authenticated” state; use session/token for subsequent API calls.
4. **Error handling**: Show generic messages; log details server-side; support “forgot password” via Cognito only.

---

### 10. Security & Hardening

- **Secrets**: No passwords or answer plaintext in client storage; only hashes in DynamoDB for Q&A.
- **Tokens**: Prefer short-lived access tokens; refresh via Cognito where applicable; pass tokens in headers (e.g. Authorization).
- **HTTPS only** for all auth endpoints.
- **Rate limiting**: On Cognito and/or API Gateway to mitigate brute force.
- **Constant-time comparison** for answers and cipher verification to reduce timing side channels.
- **TTL**: Use DynamoDB TTL for session and challenge data to auto-expire.

---

### 11. Testing & Validation

- **Unit**: Lambda logic for Caesar cipher, hash comparison, session state transitions.
- **Integration**: DynamoDB read/write, Cognito sign-up/sign-in (with test user pool), full 2nd and 3rd factor flows.
- **E2E**: Front-end flows for sign-up and sequential 3FA login; verify implicit deny when skipping a factor.

---

### 12. Optional Enhancements

- **Cognito custom auth challenge**: Integrate 2nd/3rd factor into Cognito custom auth flow (advanced).
- **Recovery**: Use Cognito “forgot password”; consider admin or verified-process to reset 2nd/3rd factor data in DynamoDB.
- **Audit**: Log factor attempts (success/failure) to CloudWatch or DynamoDB for security reviews.

---

## Summary Checklist

- [ ] DynamoDB tables (profiles, Q&A, cipher config, session/state)
- [ ] Cognito User Pool + sign-up/sign-in + optional triggers
- [ ] Lambda: session create, factor-2 Q&A verify, factor-3 challenge + verify, Caesar logic
- [ ] API Gateway (or ALB) routes to Lambda; auth on each endpoint
- [ ] Front-end: sign-up, 3-step login (Cognito → Q&A → Caesar), token/session handling
- [ ] FSM: session state in DynamoDB; strict ordering (factor N only after N-1 done)
- [ ] Security: hashed answers, constant-time compare, HTTPS, rate limiting, TTL
