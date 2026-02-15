# Penguin — Daily plan

## 2026-02-14

**Two main tasks**
1. Run and verify the local auth API (seed, uvicorn, test login then factor2 then factor3).
2. Start the front-end login flow (React app, one screen calling `/auth/login`) or start AWS setup (DynamoDB + Cognito)—pick one.

**Nice-to-do**
- Add a small script or curl examples to hit the full 3FA flow end-to-end.

---

## 2026-02-15

**Two main tasks**
1. Set up DynamoDB tables and Cognito User Pool for Module 1 auth.
2. Implement session Lambda and factor-2 (Q&A) Lambda; expose via API and enforce FSM.

**Nice-to-do**
- Sketch the front-end login flow (screens/wireframe for sign-up and 3-step login).

---

## 2026-02-16

**Two main tasks**
1. Implement factor-3 (Caesar cipher) Lambda: challenge generation, verification, Caesar encode/verify logic.
2. Wire all auth Lambdas to API Gateway; ensure FSM (session state) is enforced on every factor endpoint.

**Nice-to-do**
- Add TTL on session and challenge items in DynamoDB.

---

## 2026-02-17

**Two main tasks**
1. Build front-end sign-up flow: Cognito sign-up + post-sign-up setup (save security Q&A and Caesar config via API).
2. Build front-end 3-step login: Cognito → Q&A step → Caesar step; pass token and sessionId between steps.

**Nice-to-do**
- Add basic error messages and loading states on auth screens.

---

## 2026-02-18

**Two main tasks**
1. Harden auth: hashed Q&A, constant-time compare, HTTPS, rate limiting; verify TTL on session/challenge.
2. Add unit tests for Lambdas (Caesar, factor-2 verify) and one full 3FA integration or E2E flow.

**Nice-to-do**
- Quick pass over Module 1 checklist in `notes/Module1 implementation steps.md` and fix any gaps.
