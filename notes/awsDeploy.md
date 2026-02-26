## AWS Deploy & Test – Penguin Auth

The backend is deployed as **seven Lambda functions** (one per route: root, signup, login, factor2/question, factor2/verify, factor3/challenge, factor3/verify). The zip contains `app/` and `handlers/`; Mangum is not used in the deployed Lambdas. The API surface is unchanged.

- **Prereqs**
  - Terraform ≥ 1.0 installed.
  - AWS CLI configured with credentials and region.
  - Python 3 + `pip` installed.

- **1. Build Lambda package (from repo root)**
  - `./terraform/scripts/build_lambda.sh`
  - Produces `dist/penguin-api.zip` (app + handlers + dependencies) used by Terraform for all seven Lambdas.

- **2. Deploy Terraform stack**
  - `cd terraform`
  - `terraform init`
  - `terraform apply`

- **3. Grab outputs**
  - `terraform output api_url`
  - `terraform output cognito_user_pool_id`
  - `terraform output cognito_user_pool_client_id`
  - `terraform output user_mfa_table_name`

- **4. Point frontend at API Gateway**
  - In `frontend/.env` set `VITE_API_BASE=<api_url from Terraform>`.
  - From `frontend/`: `npm install` then `npm run dev`.

- **5. Test 3-step MFA in browser**
  - Open the frontend (Vite dev URL).
  - **Step 1:** On login screen, enter email + password.
    - Click **Sign up** to start the signup flow.
  - **Step 2 (signup):** Enter a security question and answer.
  - **Step 3 (signup):** Enter a Caesar cipher rotation key (integer 1–25). This is your personal secret key stored in DynamoDB at registration. Remember it — you will need it at login.
  - After signup, login automatically proceeds to factor 2 and factor 3.
  - **Factor 2:** Answer your security question.
  - **Factor 3:** You are shown a 4-character plaintext. Apply your rotation key (Caesar cipher) to it and submit the ciphertext. The challenge is stored in DynamoDB (`challenges` table) so it is consistent across Lambda instances.

- **6. Verify in AWS (for screenshots)**
  - Cognito User Pool: confirm the new user exists.
  - DynamoDB `users` table: confirm row with `user_id`, `email`, `role`, `question`, `answer_hash`, `rotation`.
  - DynamoDB `challenges` table: confirm a row appears during an active factor 3 challenge (it auto-expires via TTL after 10 minutes).

- **7. Minimum IAM permissions for Terraform user**
  - **DynamoDB**
    - `dynamodb:CreateTable`, `dynamodb:DescribeTable`, `dynamodb:UpdateTable`, `dynamodb:DeleteTable`
    - On `arn:aws:dynamodb:<region>:<account-id>:table/penguin-auth-*` (covers users, tokens, sessions, challenges tables).
  - **Cognito User Pool**
    - `cognito-idp:CreateUserPool`, `cognito-idp:DeleteUserPool`, `cognito-idp:UpdateUserPool`
    - `cognito-idp:CreateUserPoolClient`, `cognito-idp:DeleteUserPoolClient`, `cognito-idp:UpdateUserPoolClient`
  - **API Gateway v2 (HTTP API)**
    - `apigateway:GET`, `apigateway:POST`, `apigateway:PATCH`, `apigateway:DELETE` on HTTP APIs and stages (or `apigateway:*` for dev).
  - **Lambda**
    - `lambda:CreateFunction`, `lambda:UpdateFunctionCode`, `lambda:UpdateFunctionConfiguration`, `lambda:DeleteFunction`
  - **IAM (for Lambda role)**
    - `iam:CreateRole`, `iam:DeleteRole`, `iam:AttachRolePolicy`, `iam:DetachRolePolicy`, `iam:PutRolePolicy`, `iam:DeleteRolePolicy`
    - `iam:PassRole` for the Lambda execution role Terraform creates.
  - **CloudWatch Logs**
    - Optional for Terraform user (Lambda will also need permissions via its role):
      - `logs:CreateLogGroup`, `logs:CreateLogStream`, `logs:PutLogEvents`.
