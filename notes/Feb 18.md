## Feb 18 – Auth stack work

- Switched project auth design to AWS Cognito + Lambda + DynamoDB per requirements.
- Added Terraform resources for Cognito User Pool, SPA client, and DynamoDB `user_mfa` table.
- Updated Lambda env/IAM to use Cognito and DynamoDB instead of SQLite-only auth.
- Refactored FastAPI auth routes to call Cognito for signup/login and DynamoDB for MFA metadata.
- Kept SQLite sessions/challenges for short-lived state and local dev mode.
- Wired explicit `/auth/*` routes in API Gateway and extended frontend to support signup + AWS-backed login.

### Stepped signup flow

Signup now mirrors login with three steps (then one POST `/auth/signup` + login):

1. **Step 1 (email/password):** LoginForm; "Sign up" calls `onSignupStart({ email, password })` and advances to step 2 (no API yet).
2. **Step 2 (question creation):** SignupQuestionStep – user enters security question and answer; Back → step 1, Next → step 3.
3. **Step 3 (rotation):** SignupRotationStep – user sets Caesar rotation (1–25); Back → step 2, "Create account" → `signup()` then `login()` then into Factor 2.

Files: `SignupQuestionStep.tsx`, `SignupRotationStep.tsx`; App.tsx holds signup mode/step/signupData and wires steps; LoginForm accepts optional `onSignupStart` for stepped flow.

### Bug: “No security question set” after signup

- **Issue:** Right after the 3-step signup, the Factor 2 screen showed “No security question set” instead of the question just created. Suspected cause was different backends (signup vs Factor 2); logs showed all requests hit the same API, so backend was the same.
- **Root cause:** DynamoDB eventual consistency. Signup does `PutItem` (user_mfa); Factor 2 does `GetItem` for the question. The default `GetItem` is eventually consistent, so the read could miss the row written moments earlier.
- **Fix:** Use a consistent read when fetching MFA config: in `backend/app/aws_integration.py`, `get_user_mfa_config()` now calls `get_item(..., ConsistentRead=True)` so the row is visible immediately after signup.

