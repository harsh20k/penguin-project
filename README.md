# Penguin Auth - Three-Factor Authentication System

A secure 3FA system using AWS Cognito (password), security questions (DynamoDB), and Caesar cipher challenges.

## Quick Start

### Local Development

1. **Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
python seed_local.py  # Seeds dev user (dev@local / devpass, rotation=7)
```

2. **Frontend:**
```bash
cd frontend
npm install
npm run dev
```

3. Access at `http://localhost:5173`

### AWS Deployment

1. **Deploy Infrastructure:**
```bash
# Build Lambda package
./terraform/scripts/build_lambda.sh

# Deploy with Terraform
cd terraform
terraform init
terraform apply
```

2. **Configure Frontend:**
```bash
# Get API URL from Terraform
cd terraform
terraform output api_url

# Set in frontend/.env
echo "VITE_API_BASE=<api_url>" > ../frontend/.env
```

3. **Deploy Frontend to S3:**
```bash
# From repo root
./terraform/scripts/deploy_frontend.sh
```

4. **Access Application:**
```bash
# Get S3 website URL
cd terraform
terraform output frontend_website_url
```

## Architecture

- **Factor 1:** AWS Cognito password authentication
- **Factor 2:** Security question/answer (hashed in DynamoDB)
- **Factor 3:** Caesar cipher challenge (user rotation key 1-25)

See `notes/arch/Architecture.md` for detailed architecture.

## Features

- Simple, clean homepage after successful authentication
- Role-based signup (Client/Dispatch)
- Session management with 24h token TTL
- Public S3 static website hosting (no CloudFront complexity)
- Serverless backend with Lambda + API Gateway

## Signup Flow

1. Enter email and password
2. Select role (Client or Dispatch Operator)
3. Create security question and answer
4. Choose Caesar cipher rotation key (1-25)
5. Auto-login and complete all three factors

## Security

- Security answers stored as SHA-256 hashes
- Constant-time comparison for cipher verification
- 10-minute TTL on Caesar challenges
- Rotation keys never returned after signup
- Simple public S3 hosting for frontend
