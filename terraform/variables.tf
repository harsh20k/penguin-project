variable "aws_region" {
  description = "AWS region for all resources"
  type        = string
  default     = "us-east-1"
}

variable "lambda_runtime" {
  description = "Lambda runtime identifier"
  type        = string
  default     = "python3.12"
}

variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
  default     = "penguin-auth"
}

variable "environment" {
  description = "Environment label (e.g. dev, prod)"
  type        = string
  default     = "dev"
}
