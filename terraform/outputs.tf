output "api_url" {
  description = "API Gateway HTTP API invoke URL (use this as the backend base URL)"
  value       = aws_apigatewayv2_stage.default.invoke_url
}

output "lambda_arn" {
  description = "ARN of the root Penguin Auth API Lambda function"
  value       = aws_lambda_function.root.arn
}

output "lambda_name" {
  description = "Name of the root Lambda function"
  value       = aws_lambda_function.root.function_name
}

output "cognito_user_pool_id" {
  description = "ID of the Cognito User Pool for auth"
  value       = aws_cognito_user_pool.users.id
}

output "cognito_user_pool_client_id" {
  description = "App client ID for the SPA"
  value       = aws_cognito_user_pool_client.spa.id
}

output "user_mfa_table_name" {
  description = "DynamoDB table name storing MFA metadata"
  value       = aws_dynamodb_table.user_mfa.name
}

output "frontend_bucket_name" {
  description = "S3 bucket name for frontend static assets"
  value       = aws_s3_bucket.frontend.id
}

output "frontend_website_url" {
  description = "S3 website endpoint URL for the frontend"
  value       = "http://${aws_s3_bucket_website_configuration.frontend.website_endpoint}"
}
