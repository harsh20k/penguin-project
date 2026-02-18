terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Local state by default. For team use, uncomment and set bucket/key:
  # backend "s3" {
  #   bucket         = "your-terraform-state-bucket"
  #   key            = "penguin-auth/terraform.tfstate"
  #   region         = "us-east-1"
  #   dynamodb_table = "terraform-locks"
  # }
}

provider "aws" {
  region = var.aws_region
}
