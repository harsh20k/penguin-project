# Terraform: Penguin Auth API on AWS Lambda

This directory deploys the Penguin Auth FastAPI backend as a single AWS Lambda behind an API Gateway HTTP API.

In the deployed configuration, authentication uses **AWS Cognito + Lambda + DynamoDB**:

- **Cognito User Pool** – username/password auth for clients/admins.
- **DynamoDB** – stores MFA metadata (security Q&A and Caesar rotation).
- **API Gateway** – exposes `/auth/*` endpoints to the React frontend.

## Prerequisites

- [Terraform](https://www.terraform.io/downloads) >= 1.0
- AWS CLI configured (credentials and region)
- Python 3 with `pip` (for building the Lambda zip)

## Build and deploy

1. **Build the Lambda deployment package** (from the repo root):

   ```bash
   ./terraform/scripts/build_lambda.sh
   ```

   This produces `dist/penguin-api.zip` (app code + dependencies). Terraform expects this file to exist before apply.

2. **Initialize and apply** (from this directory):

   ```bash
   cd terraform
   terraform init
   terraform plan   # optional
   terraform apply
   ```

3. **Get the API URL**:

   ```bash
   terraform output api_url
   ```

   Use this URL as the backend base (e.g. set `VITE_API_BASE` in the frontend, or call `https://<api_url>/auth/login` etc.).

4. **Get Cognito and DynamoDB details**:

   ```bash
   terraform output cognito_user_pool_id
   terraform output cognito_user_pool_client_id
   terraform output user_mfa_table_name
   ```

## Variables

- `aws_region` (default: `us-east-1`) – region for all resources
- `lambda_runtime` (default: `python3.12`) – Lambda runtime
- `project_name` (default: `penguin-auth`) – prefix for resource names
- `environment` (default: `dev`) – suffix for resource names

Override via `-var` or a `.tfvars` file.

## Persistence (important)

The Lambda runs with `DB_PATH=/tmp/local.db` for session and Caesar challenge state. **SQLite in `/tmp` is ephemeral**: data is lost when the Lambda execution environment is recycled. This is acceptable for short-lived auth sessions.

User and MFA configuration is stored in **DynamoDB**, which is persistent and managed by AWS.

For production-grade persistence of session/challenge data you could:

- Attach an EFS access point to the Lambda and set `DB_PATH` to the mount path so SQLite uses a persistent file, or
- Move session/challenge data into DynamoDB and remove SQLite from the Lambda entirely.

## Remote state (optional)

To use S3 + DynamoDB for Terraform state, uncomment and fill the `backend "s3"` block in `main.tf`, then run `terraform init -migrate-state` if you already have local state.
