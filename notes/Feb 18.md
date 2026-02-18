## Feb 18 – Auth stack work

- Switched project auth design to AWS Cognito + Lambda + DynamoDB per requirements.
- Added Terraform resources for Cognito User Pool, SPA client, and DynamoDB `user_mfa` table.
- Updated Lambda env/IAM to use Cognito and DynamoDB instead of SQLite-only auth.
- Refactored FastAPI auth routes to call Cognito for signup/login and DynamoDB for MFA metadata.
- Kept SQLite sessions/challenges for short-lived state and local dev mode.
- Wired explicit `/auth/*` routes in API Gateway and extended frontend to support signup + AWS-backed login.

