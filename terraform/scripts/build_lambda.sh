#!/usr/bin/env bash
# Build Lambda deployment zip: app code + dependencies.
# Run from repo root: ./terraform/scripts/build_lambda.sh
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BACKEND="${REPO_ROOT}/backend"
BUILD_DIR="${REPO_ROOT}/dist/build"
DIST_DIR="${REPO_ROOT}/dist"
ZIP_NAME="penguin-api.zip"

mkdir -p "${BUILD_DIR}"
rm -rf "${BUILD_DIR:?}"/*
cd "${BUILD_DIR}"

# Copy application code
cp -r "${BACKEND}/app" .
cp "${BACKEND}/lambda_handler.py" .

# Install dependencies for Lambda (Amazon Linux x86_64); avoid host-platform binaries (e.g. pydantic_core on macOS)
pip install --quiet --target . \
  --platform manylinux2014_x86_64 \
  --python-version 3.12 \
  --only-binary=:all: \
  -r "${BACKEND}/requirements.txt"

# Remove unneeded bits to reduce size
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true

# Zip (contents of BUILD_DIR must be at zip root so handler is lambda_handler.handler)
mkdir -p "${DIST_DIR}"
cd "${BUILD_DIR}"
zip -r -q "${DIST_DIR}/${ZIP_NAME}" . -x "*.pyc" -x "*__pycache__*"
echo "Built ${DIST_DIR}/${ZIP_NAME}"
