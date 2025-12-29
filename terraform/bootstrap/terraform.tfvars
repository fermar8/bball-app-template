# AWS Configuration
aws_region = "eu-west-3"

# S3 State Backend
state_bucket_name = "tfstate-590183661886-eu-west-3"  # Make this globally unique

# DynamoDB Lock Table
lock_table_name = "terraform-state-lock"

# GitHub Repository Configuration
github_org  = "fermar8"
github_repo = "bball-app-template"

# OIDC Provider
create_oidc_provider       = true
existing_oidc_provider_arn = "" # Only needed if create_oidc_provider = false
