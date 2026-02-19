data "aws_caller_identity" "current" {}

locals {
  lambda_zip_path = "${path.module}/../dist/penguin-api.zip"
  lambda_name     = "${var.project_name}-api-${var.environment}"
}

resource "aws_iam_role" "lambda" {
  name = "${local.lambda_name}-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_lambda_function" "api" {
  filename         = local.lambda_zip_path
  function_name    = local.lambda_name
  role             = aws_iam_role.lambda.arn
  handler          = "lambda_handler.handler"
  runtime          = var.lambda_runtime
  source_code_hash = filebase64sha256(local.lambda_zip_path)
  timeout          = 30
  memory_size      = 256

  environment {
    variables = {
      DB_PATH               = "/tmp/local.db"
      COGNITO_USER_POOL_ID   = aws_cognito_user_pool.users.id
      COGNITO_CLIENT_ID      = aws_cognito_user_pool_client.spa.id
      DDB_USER_TABLE_NAME    = aws_dynamodb_table.user_mfa.name
      TOKEN_TABLE_NAME       = aws_dynamodb_table.tokens.name
      SESSIONS_TABLE_NAME    = aws_dynamodb_table.sessions.name
    }
  }
}
