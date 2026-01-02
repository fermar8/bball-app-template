terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# S3 Bucket for Terraform State
resource "aws_s3_bucket" "terraform_state" {
  bucket = var.state_bucket_name

  tags = {
    Name      = "Terraform State Bucket"
    Project   = "bball-app"
    ManagedBy = "terraform"
  }
}

# Enable versioning for state bucket
resource "aws_s3_bucket_versioning" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Enable encryption for state bucket
resource "aws_s3_bucket_server_side_encryption_configuration" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Block public access to state bucket
resource "aws_s3_bucket_public_access_block" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# DynamoDB Table for State Locking
resource "aws_dynamodb_table" "terraform_locks" {
  name         = var.lock_table_name
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }

  tags = {
    Name      = "Terraform State Lock Table"
    Project   = "bball-app"
    ManagedBy = "terraform"
  }
}

# GitHub Actions OIDC Provider
resource "aws_iam_openid_connect_provider" "github" {
  count = var.create_oidc_provider ? 1 : 0

  url = "https://token.actions.githubusercontent.com"

  client_id_list = [
    "sts.amazonaws.com",
  ]

  thumbprint_list = [
    "6938fd4d98bab03faadb97b34396831e3780aea1",
    "1c58a3a8518e8759bf075b76b750d4f2df264fcd"
  ]

  tags = {
    Name      = "github-actions-oidc"
    ManagedBy = "terraform"
  }
}

# IAM Role for GitHub Actions Pipeline
resource "aws_iam_role" "github_actions_pipeline" {
  name        = "bball-app-template-pipeline-role"
  description = "Role for GitHub Actions pipeline to deploy bball-app resources"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = var.create_oidc_provider ? aws_iam_openid_connect_provider.github[0].arn : var.existing_oidc_provider_arn
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals = {
            "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
          }
          StringLike = {
            "token.actions.githubusercontent.com:sub" = "repo:${var.github_org}/${var.github_repo}:*"
          }
        }
      }
    ]
  })

  tags = {
    Name      = "bball-app-template-pipeline-role"
    ManagedBy = "terraform"
    Purpose   = "GitHub Actions Pipeline"
  }
}

# IAM Policy for Lambda Management
resource "aws_iam_policy" "lambda_management" {
  name        = "bball-app-template-lambda-management"
  description = "Permissions for managing Lambda functions and related resources"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "LambdaFunctionManagement"
        Effect = "Allow"
        Action = [
          "lambda:CreateFunction",
          "lambda:DeleteFunction",
          "lambda:GetFunction",
          "lambda:GetFunctionConfiguration",
          "lambda:UpdateFunctionCode",
          "lambda:UpdateFunctionConfiguration",
          "lambda:ListFunctions",
          "lambda:ListVersionsByFunction",
          "lambda:ListTags",
          "lambda:TagResource",
          "lambda:UntagResource",
          "lambda:PublishVersion",
          "lambda:GetPolicy",
          "lambda:AddPermission",
          "lambda:RemovePermission",
          "lambda:GetAlias",
          "lambda:ListAliases",
          "lambda:GetFunctionCodeSigningConfig",
          "lambda:GetFunctionEventInvokeConfig",
          "lambda:ListFunctionEventInvokeConfigs"
        ]
        Resource = [
          "arn:aws:lambda:${var.aws_region}:*:function:bball-app-template-*"
        ]
      }
    ]
  })

  tags = {
    Name      = "bball-app-template-lambda-management"
    ManagedBy = "terraform"
  }
}

# IAM Policy for IAM Management (for Lambda execution roles)
resource "aws_iam_policy" "iam_management" {
  name        = "bball-app-template-iam-management"
  description = "Permissions for managing IAM roles and policies for Lambda"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "IAMRoleManagement"
        Effect = "Allow"
        Action = [
          "iam:CreateRole",
          "iam:DeleteRole",
          "iam:GetRole",
          "iam:GetRolePolicy",
          "iam:ListRolePolicies",
          "iam:ListAttachedRolePolicies",
          "iam:ListInstanceProfilesForRole",
          "iam:ListRoleTags",
          "iam:PassRole",
          "iam:TagRole",
          "iam:UntagRole",
          "iam:UpdateRole",
          "iam:UpdateAssumeRolePolicy"
        ]
        Resource = [
          "arn:aws:iam::*:role/bball-app-template-*"
        ]
      },
      {
        Sid    = "IAMPolicyManagement"
        Effect = "Allow"
        Action = [
          "iam:CreatePolicy",
          "iam:DeletePolicy",
          "iam:GetPolicy",
          "iam:GetPolicyVersion",
          "iam:ListPolicyVersions",
          "iam:CreatePolicyVersion",
          "iam:DeletePolicyVersion"
        ]
        Resource = [
          "arn:aws:iam::*:policy/bball-app-template-*"
        ]
      },
      {
        Sid    = "IAMPolicyAttachment"
        Effect = "Allow"
        Action = [
          "iam:AttachRolePolicy",
          "iam:DetachRolePolicy"
        ]
        Resource = [
          "arn:aws:iam::*:role/bball-app-template-*"
        ]
      }
    ]
  })

  tags = {
    Name      = "bball-app-template-iam-management"
    ManagedBy = "terraform"
  }
}

# IAM Policy for CloudWatch Logs
resource "aws_iam_policy" "cloudwatch_logs" {
  name        = "bball-app-template-cloudwatch-logs"
  description = "Permissions for managing CloudWatch log groups"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "CloudWatchLogsManagement"
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:DeleteLogGroup",
          "logs:DescribeLogGroups",
          "logs:ListTagsLogGroup",
          "logs:ListTagsForResource",
          "logs:TagLogGroup",
          "logs:UntagLogGroup",
          "logs:PutRetentionPolicy",
          "logs:DeleteRetentionPolicy"
        ]
        Resource = [
          "arn:aws:logs:${var.aws_region}:*:log-group:/aws/lambda/bball-app-template-*",
          "arn:aws:logs:${var.aws_region}:*:log-group:/aws/lambda/bball-app-template-*:*",
          "arn:aws:logs:${var.aws_region}:*:log-group::log-stream:*"
        ]
      }
    ]
  })

  tags = {
    Name      = "bball-app-template-cloudwatch-logs"
    ManagedBy = "terraform"
  }
}

# IAM Policy for S3 (Terraform State)
resource "aws_iam_policy" "s3_state_access" {
  name        = "bball-app-template-s3-state-access"
  description = "Permissions for S3 terraform state access"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "S3StateBackend"
        Effect = "Allow"
        Action = [
          "s3:ListBucket",
          "s3:GetBucketVersioning"
        ]
        Resource = [
          aws_s3_bucket.terraform_state.arn
        ]
      },
      {
        Sid    = "S3StateAccess"
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ]
        Resource = [
          "${aws_s3_bucket.terraform_state.arn}/*"
        ]
      }
    ]
  })

  tags = {
    Name      = "bball-app-template-s3-state-access"
    ManagedBy = "terraform"
  }
}

# IAM Policy for DynamoDB (Terraform State Locking)
resource "aws_iam_policy" "dynamodb_state_lock" {
  name        = "bball-app-template-dynamodb-state-lock"
  description = "Permissions for DynamoDB state locking"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "DynamoDBStateLock"
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:DeleteItem",
          "dynamodb:DescribeTable"
        ]
        Resource = [
          aws_dynamodb_table.terraform_locks.arn
        ]
      }
    ]
  })

  tags = {
    Name      = "bball-app-template-dynamodb-state-lock"
    ManagedBy = "terraform"
  }
}

# IAM Policy for DynamoDB Table Management
resource "aws_iam_policy" "dynamodb_management" {
  name        = "bball-app-template-dynamodb-management"
  description = "Permissions for managing DynamoDB tables"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "DynamoDBTableManagement"
        Effect = "Allow"
        Action = [
          "dynamodb:CreateTable",
          "dynamodb:DeleteTable",
          "dynamodb:DescribeTable",
          "dynamodb:DescribeContinuousBackups",
          "dynamodb:DescribeTimeToLive",
          "dynamodb:ListTagsOfResource",
          "dynamodb:TagResource",
          "dynamodb:UntagResource",
          "dynamodb:UpdateTable",
          "dynamodb:UpdateTimeToLive",
          "dynamodb:UpdateContinuousBackups"
        ]
        Resource = [
          "arn:aws:dynamodb:${var.aws_region}:*:table/bball-app-*",
          "arn:aws:dynamodb:${var.aws_region}:*:table/${var.project_name}-*"
        ]
      }
    ]
  })

  tags = {
    Name      = "bball-app-template-dynamodb-management"
    ManagedBy = "terraform"
  }
}

# IAM Policy for Additional AWS Services (EventBridge, SNS, SQS, etc.)
resource "aws_iam_policy" "additional_services" {
  name        = "bball-app-template-additional-services"
  description = "Permissions for EventBridge Scheduler, SNS, SQS, and other common services"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "EventBridgeScheduler"
        Effect = "Allow"
        Action = [
          "scheduler:CreateSchedule",
          "scheduler:DeleteSchedule",
          "scheduler:GetSchedule",
          "scheduler:ListSchedules",
          "scheduler:UpdateSchedule",
          "scheduler:TagResource",
          "scheduler:UntagResource",
          "scheduler:ListTagsForResource"
        ]
        Resource = [
          "arn:aws:scheduler:${var.aws_region}:*:schedule/default/bball-app-*",
          "arn:aws:scheduler:${var.aws_region}:*:schedule/default/${var.project_name}-*"
        ]
      },
      {
        Sid    = "SNSTopicManagement"
        Effect = "Allow"
        Action = [
          "sns:CreateTopic",
          "sns:DeleteTopic",
          "sns:GetTopicAttributes",
          "sns:SetTopicAttributes",
          "sns:Subscribe",
          "sns:Unsubscribe",
          "sns:ListSubscriptionsByTopic",
          "sns:TagResource",
          "sns:UntagResource"
        ]
        Resource = [
          "arn:aws:sns:${var.aws_region}:*:bball-app-*",
          "arn:aws:sns:${var.aws_region}:*:${var.project_name}-*"
        ]
      },
      {
        Sid    = "SQSQueueManagement"
        Effect = "Allow"
        Action = [
          "sqs:CreateQueue",
          "sqs:DeleteQueue",
          "sqs:GetQueueAttributes",
          "sqs:SetQueueAttributes",
          "sqs:TagQueue",
          "sqs:UntagQueue",
          "sqs:ListQueueTags"
        ]
        Resource = [
          "arn:aws:sqs:${var.aws_region}:*:bball-app-*",
          "arn:aws:sqs:${var.aws_region}:*:${var.project_name}-*"
        ]
      },
      {
        Sid    = "ApiGatewayManagement"
        Effect = "Allow"
        Action = [
          "apigateway:GET",
          "apigateway:POST",
          "apigateway:PUT",
          "apigateway:PATCH",
          "apigateway:DELETE"
        ]
        Resource = [
          "arn:aws:apigateway:${var.aws_region}::/restapis",
          "arn:aws:apigateway:${var.aws_region}::/restapis/*"
        ]
      },
      {
        Sid    = "S3BucketManagement"
        Effect = "Allow"
        Action = [
          "s3:CreateBucket",
          "s3:DeleteBucket",
          "s3:GetBucketPolicy",
          "s3:PutBucketPolicy",
          "s3:DeleteBucketPolicy",
          "s3:GetBucketVersioning",
          "s3:PutBucketVersioning",
          "s3:GetBucketTagging",
          "s3:PutBucketTagging",
          "s3:GetBucketPublicAccessBlock",
          "s3:PutBucketPublicAccessBlock",
          "s3:GetEncryptionConfiguration",
          "s3:PutEncryptionConfiguration"
        ]
        Resource = [
          "arn:aws:s3:::bball-app-*",
          "arn:aws:s3:::${var.project_name}-*"
        ]
      }
    ]
  })

  tags = {
    Name      = "bball-app-template-additional-services"
    ManagedBy = "terraform"
  }
}

# Attach all policies to the pipeline role
resource "aws_iam_role_policy_attachment" "lambda_management" {
  role       = aws_iam_role.github_actions_pipeline.name
  policy_arn = aws_iam_policy.lambda_management.arn
}

resource "aws_iam_role_policy_attachment" "iam_management" {
  role       = aws_iam_role.github_actions_pipeline.name
  policy_arn = aws_iam_policy.iam_management.arn
}

resource "aws_iam_role_policy_attachment" "cloudwatch_logs" {
  role       = aws_iam_role.github_actions_pipeline.name
  policy_arn = aws_iam_policy.cloudwatch_logs.arn
}

resource "aws_iam_role_policy_attachment" "s3_state_access" {
  role       = aws_iam_role.github_actions_pipeline.name
  policy_arn = aws_iam_policy.s3_state_access.arn
}

resource "aws_iam_role_policy_attachment" "dynamodb_state_lock" {
  role       = aws_iam_role.github_actions_pipeline.name
  policy_arn = aws_iam_policy.dynamodb_state_lock.arn
}

resource "aws_iam_role_policy_attachment" "dynamodb_management" {
  role       = aws_iam_role.github_actions_pipeline.name
  policy_arn = aws_iam_policy.dynamodb_management.arn
}

resource "aws_iam_role_policy_attachment" "additional_services" {
  role       = aws_iam_role.github_actions_pipeline.name
  policy_arn = aws_iam_policy.additional_services.arn
}
