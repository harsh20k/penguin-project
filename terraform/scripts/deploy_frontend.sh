#!/bin/bash
set -e

# Build and deploy frontend to S3
# Usage: ./deploy_frontend.sh

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}==> Building frontend...${NC}"
cd frontend
npm run build

echo -e "${BLUE}==> Getting S3 bucket name from Terraform outputs...${NC}"
cd ../terraform
BUCKET_NAME=$(terraform output -raw frontend_bucket_name)
WEBSITE_URL=$(terraform output -raw frontend_website_url)

echo -e "${BLUE}==> Uploading to S3 bucket: ${BUCKET_NAME}${NC}"
aws s3 sync ../frontend/dist/ s3://${BUCKET_NAME}/ --delete

echo -e "${GREEN}==> Frontend deployed successfully!${NC}"
echo -e "${GREEN}==> Website URL: ${WEBSITE_URL}${NC}"
