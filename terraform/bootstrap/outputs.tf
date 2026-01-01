output "state_bucket_name" {
  description = "Name of the S3 bucket for Terraform state"
  value       = aws_s3_bucket.terraform_state.id
}

output "state_bucket_arn" {
  description = "ARN of the S3 bucket for Terraform state"
  value       = aws_s3_bucket.terraform_state.arn
}

output "lock_table_name" {
  description = "Name of the DynamoDB table for state locking"
  value       = aws_dynamodb_table.terraform_locks.id
}

output "lock_table_arn" {
  description = "ARN of the DynamoDB table for state locking"
  value       = aws_dynamodb_table.terraform_locks.arn
}

output "pipeline_role_arn" {
  description = "ARN of the GitHub Actions pipeline role"
  value       = aws_iam_role.github_actions_pipeline.arn
}

output "pipeline_role_name" {
  description = "Name of the GitHub Actions pipeline role"
  value       = aws_iam_role.github_actions_pipeline.name
}

# DynamoDB outputs
output "dynamodb_table_nonlive_name" {
  description = "Name of the DynamoDB table for nonlive environment"
  value       = aws_dynamodb_table.nonlive.name
}

output "dynamodb_table_nonlive_arn" {
  description = "ARN of the DynamoDB table for nonlive environment"
  value       = aws_dynamodb_table.nonlive.arn
}

output "dynamodb_table_live_name" {
  description = "Name of the DynamoDB table for live environment"
  value       = aws_dynamodb_table.live.name
}

output "dynamodb_table_live_arn" {
  description = "ARN of the DynamoDB table for live environment"
  value       = aws_dynamodb_table.live.arn
}

output "oidc_provider_arn" {
  description = "ARN of the GitHub OIDC provider"
  value       = var.create_oidc_provider ? aws_iam_openid_connect_provider.github[0].arn : var.existing_oidc_provider_arn
}

output "backend_config" {
  description = "Backend configuration to use in other Terraform projects"
  value = <<-EOT
    terraform {
      backend "s3" {
        bucket         = "${aws_s3_bucket.terraform_state.id}"
        key            = "${var.github_repo}/terraform.tfstate"
        region         = "${var.aws_region}"
        dynamodb_table = "${aws_dynamodb_table.terraform_locks.id}"
        encrypt        = true
      }
    }
  EOT
}
