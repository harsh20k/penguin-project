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
  - In `frontend/.env.local` set `VITE_API_BASE=<api_url from Terraform>`.
  - From `frontend/`: `npm install` then `npm run dev`.

- **5. Test 3-step MFA in browser**
  - Open the frontend (Vite dev URL).
  - **Step 1:** On login screen, enter email + password.
    - Click **Sign up** to hit `/auth/signup` then `/auth/login` (Cognito + DynamoDB).
  - **Step 2:** Answer security question (calls `/auth/factor2/question` + `/auth/factor2/verify`).
  - **Step 3:** Solve Caesar challenge (calls `/auth/factor3/challenge` + `/auth/factor3/verify`) until “Authenticated”.

- **6. Verify in AWS (for screenshots)**
  - Cognito User Pool: confirm the new user exists.
  - DynamoDB `user_mfa` table: confirm row with `user_id`, `email`, `role`, `question`, `answer_hash`, `rotation`.

- **7. Minimum IAM permissions for Terraform user**
  - **DynamoDB**
    - `dynamodb:CreateTable`, `dynamodb:DescribeTable`, `dynamodb:UpdateTable`, `dynamodb:DeleteTable`
    - On `arn:aws:dynamodb:<region>:<account-id>:table/penguin-auth-users-*` (or broader for dev).
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

