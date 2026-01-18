variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "eu-west-3"
}

variable "state_bucket_name" {
  description = "Name of the S3 bucket for Terraform state"
  type        = string
}

variable "nba_data_bucket_name" {
  description = "S3 bucket name for NBA data storage"
  type        = string
  default     = "bball-app-nba-data"
}

variable "lock_table_name" {
  description = "Name of the DynamoDB table for state locking"
  type        = string
  default     = "bball-app-terraform-locks"
}

variable "github_org" {
  description = "GitHub organization or username"
  type        = string
}

variable "github_repo" {
  description = "GitHub repository name"
  type        = string
}

variable "create_oidc_provider" {
  description = "Whether to create the GitHub OIDC provider (set to false if it already exists)"
  type        = bool
  default     = true
}

variable "existing_oidc_provider_arn" {
  description = "ARN of existing GitHub OIDC provider (required if create_oidc_provider is false)"
  type        = string
  default     = ""
}

variable "project_name" {
  description = "Name of the project (used for resource naming)"
  type        = string
  default     = "bball-app"
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default = {
    Project   = "bball-app"
    ManagedBy = "terraform"
  }
}
