data "aws_caller_identity" "current" {}

locals {
  lambda_zip_path = "${path.module}/../dist/penguin-api.zip"
  lambda_name     = "${var.project_name}-api-${var.environment}"

  lambda_env = {
    DB_PATH                  = "/tmp/local.db"
    COGNITO_USER_POOL_ID     = aws_cognito_user_pool.users.id
    COGNITO_CLIENT_ID        = aws_cognito_user_pool_client.spa.id
    DDB_USER_TABLE_NAME      = aws_dynamodb_table.user_mfa.name
    TOKEN_TABLE_NAME         = aws_dynamodb_table.tokens.name
    SESSIONS_TABLE_NAME      = aws_dynamodb_table.sessions.name
    CHALLENGES_TABLE_NAME    = aws_dynamodb_table.challenges.name
  }

  lambda_handlers = {
    root             = "handlers.root.handler"
    signup           = "handlers.signup.handler"
    login            = "handlers.login.handler"
    factor2_question = "handlers.factor2_question.handler"
    factor2_verify   = "handlers.factor2_verify.handler"
    factor3_challenge = "handlers.factor3_challenge.handler"
    factor3_verify   = "handlers.factor3_verify.handler"
  }
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

resource "aws_lambda_function" "root" {
  filename         = local.lambda_zip_path
  function_name    = "${local.lambda_name}-root"
  role             = aws_iam_role.lambda.arn
  handler          = local.lambda_handlers.root
  runtime          = var.lambda_runtime
  source_code_hash = filebase64sha256(local.lambda_zip_path)
  timeout          = 30
  memory_size      = 256

  environment {
    variables = local.lambda_env
  }
}

resource "aws_lambda_function" "signup" {
  filename         = local.lambda_zip_path
  function_name    = "${local.lambda_name}-signup"
  role             = aws_iam_role.lambda.arn
  handler          = local.lambda_handlers.signup
  runtime          = var.lambda_runtime
  source_code_hash = filebase64sha256(local.lambda_zip_path)
  timeout          = 30
  memory_size      = 256

  environment {
    variables = local.lambda_env
  }
}

resource "aws_lambda_function" "login" {
  filename         = local.lambda_zip_path
  function_name    = "${local.lambda_name}-login"
  role             = aws_iam_role.lambda.arn
  handler          = local.lambda_handlers.login
  runtime          = var.lambda_runtime
  source_code_hash = filebase64sha256(local.lambda_zip_path)
  timeout          = 30
  memory_size      = 256

  environment {
    variables = local.lambda_env
  }
}

resource "aws_lambda_function" "factor2_question" {
  filename         = local.lambda_zip_path
  function_name    = "${local.lambda_name}-factor2-question"
  role             = aws_iam_role.lambda.arn
  handler          = local.lambda_handlers.factor2_question
  runtime          = var.lambda_runtime
  source_code_hash = filebase64sha256(local.lambda_zip_path)
  timeout          = 30
  memory_size      = 256

  environment {
    variables = local.lambda_env
  }
}

resource "aws_lambda_function" "factor2_verify" {
  filename         = local.lambda_zip_path
  function_name    = "${local.lambda_name}-factor2-verify"
  role             = aws_iam_role.lambda.arn
  handler          = local.lambda_handlers.factor2_verify
  runtime          = var.lambda_runtime
  source_code_hash = filebase64sha256(local.lambda_zip_path)
  timeout          = 30
  memory_size      = 256

  environment {
    variables = local.lambda_env
  }
}

resource "aws_lambda_function" "factor3_challenge" {
  filename         = local.lambda_zip_path
  function_name    = "${local.lambda_name}-factor3-challenge"
  role             = aws_iam_role.lambda.arn
  handler          = local.lambda_handlers.factor3_challenge
  runtime          = var.lambda_runtime
  source_code_hash = filebase64sha256(local.lambda_zip_path)
  timeout          = 30
  memory_size      = 256

  environment {
    variables = local.lambda_env
  }
}

resource "aws_lambda_function" "factor3_verify" {
  filename         = local.lambda_zip_path
  function_name    = "${local.lambda_name}-factor3-verify"
  role             = aws_iam_role.lambda.arn
  handler          = local.lambda_handlers.factor3_verify
  runtime          = var.lambda_runtime
  source_code_hash = filebase64sha256(local.lambda_zip_path)
  timeout          = 30
  memory_size      = 256

  environment {
    variables = local.lambda_env
  }
}
