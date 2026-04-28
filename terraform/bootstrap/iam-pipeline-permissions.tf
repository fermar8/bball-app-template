# IAM Policy for Lambda Management
resource "aws_iam_policy" "lambda_management" {
  name        = "${var.project_name}-template-lambda-management"
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
          "arn:aws:lambda:${var.aws_region}:*:function:${var.project_name}-*"
        ]
      },
      {
        Sid    = "LambdaEventSourceMapping"
        Effect = "Allow"
        Action = [
          "lambda:CreateEventSourceMapping",
          "lambda:UpdateEventSourceMapping",
          "lambda:DeleteEventSourceMapping",
          "lambda:GetEventSourceMapping",
          "lambda:ListEventSourceMappings",
          "lambda:ListTags",
          "lambda:TagResource",
          "lambda:UntagResource"
        ]
        Resource = [
          "arn:aws:lambda:${var.aws_region}:*:event-source-mapping:*"
        ]
      }
    ]
  })

  tags = {
    Name      = "${var.project_name}-template-lambda-management"
    ManagedBy = "terraform"
  }
}

# IAM Policy for IAM Management (for Lambda execution roles and EC2 instance profiles)
resource "aws_iam_policy" "iam_management" {
  name        = "${var.project_name}-template-iam-management"
  description = "Permissions for managing IAM roles and policies"

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
          "arn:aws:iam::*:role/${var.project_name}-*"
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
          "iam:DeletePolicyVersion",
          "iam:TagPolicy",
          "iam:UntagPolicy"
        ]
        Resource = [
          "arn:aws:iam::*:policy/${var.project_name}-*"
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
          "arn:aws:iam::*:role/${var.project_name}-*"
        ]
      },
      {
        Sid    = "IAMInlinePolicyManagement"
        Effect = "Allow"
        Action = [
          "iam:PutRolePolicy",
          "iam:DeleteRolePolicy"
        ]
        Resource = [
          "arn:aws:iam::*:role/${var.project_name}-*"
        ]
      },
      {
        Sid    = "InstanceProfileManagement"
        Effect = "Allow"
        Action = [
          "iam:CreateInstanceProfile",
          "iam:DeleteInstanceProfile",
          "iam:GetInstanceProfile",
          "iam:ListInstanceProfiles",
          "iam:AddRoleToInstanceProfile",
          "iam:RemoveRoleFromInstanceProfile",
          "iam:ListInstanceProfilesForRole",
          "iam:TagInstanceProfile",
          "iam:UntagInstanceProfile"
        ]
        Resource = "arn:aws:iam::*:instance-profile/${var.project_name}-*"
      }
    ]
  })

  tags = {
    Name      = "${var.project_name}-template-iam-management"
    ManagedBy = "terraform"
  }
}

# IAM Policy for CloudWatch (Logs and Alarms)
# Consolidated: cloudwatch_logs + cloudwatch_alarms + cloudwatch_logs_ec2
resource "aws_iam_policy" "cloudwatch_management" {
  name        = "${var.project_name}-template-cloudwatch-management"
  description = "Permissions for managing CloudWatch log groups and alarms for Lambda and EC2 services"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "CloudWatchLogsLambda"
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:DeleteLogGroup",
          "logs:DescribeLogGroups",
          "logs:ListTagsLogGroup",
          "logs:ListTagsForResource",
          "logs:TagLogGroup",
          "logs:UntagLogGroup",
          "logs:TagResource",
          "logs:UntagResource",
          "logs:PutRetentionPolicy",
          "logs:DeleteRetentionPolicy"
        ]
        Resource = [
          "arn:aws:logs:${var.aws_region}:*:log-group:/aws/lambda/${var.project_name}-*",
          "arn:aws:logs:${var.aws_region}:*:log-group:/aws/lambda/${var.project_name}-*:*",
          "arn:aws:logs:${var.aws_region}:*:log-group::log-stream:*"
        ]
      },
      {
        Sid    = "CloudWatchLogsEC2"
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:DeleteLogGroup",
          "logs:DescribeLogGroups",
          "logs:ListTagsLogGroup",
          "logs:ListTagsForResource",
          "logs:TagLogGroup",
          "logs:UntagLogGroup",
          "logs:TagResource",
          "logs:UntagResource",
          "logs:PutRetentionPolicy",
          "logs:DeleteRetentionPolicy"
        ]
        Resource = [
          "arn:aws:logs:${var.aws_region}:*:log-group:/${var.project_name}/*",
          "arn:aws:logs:${var.aws_region}:*:log-group:/${var.project_name}/*:*"
        ]
      },
      {
        Sid    = "CloudWatchMetricFilters"
        Effect = "Allow"
        Action = [
          "logs:PutMetricFilter",
          "logs:DeleteMetricFilter",
          "logs:DescribeMetricFilters"
        ]
        Resource = [
          "arn:aws:logs:${var.aws_region}:*:log-group:/aws/lambda/${var.project_name}-*",
          "arn:aws:logs:${var.aws_region}:*:log-group:/aws/lambda/${var.project_name}-*:*",
          "arn:aws:logs:${var.aws_region}:*:log-group:/${var.project_name}/*",
          "arn:aws:logs:${var.aws_region}:*:log-group:/${var.project_name}/*:*"
        ]
      },
      {
        Sid    = "CloudWatchAlarmsManagement"
        Effect = "Allow"
        Action = [
          "cloudwatch:PutMetricAlarm",
          "cloudwatch:DeleteAlarms",
          "cloudwatch:DescribeAlarms",
          "cloudwatch:ListTagsForResource",
          "cloudwatch:TagResource",
          "cloudwatch:UntagResource"
        ]
        Resource = "arn:aws:cloudwatch:${var.aws_region}:*:alarm:${var.project_name}-*"
      }
    ]
  })

  tags = {
    Name      = "${var.project_name}-template-cloudwatch-management"
    ManagedBy = "terraform"
  }
}

# IAM Policy for S3 Management (State, Buckets, NBA Data)
# Consolidated: s3_state_access + s3_bucket_management + pipeline_s3_access
resource "aws_iam_policy" "s3_management" {
  name        = "${var.project_name}-template-s3-management"
  description = "Permissions for S3 terraform state, bucket management, and NBA data access"

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
          "s3:PutEncryptionConfiguration",
          "s3:GetLifecycleConfiguration",
          "s3:PutLifecycleConfiguration",
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::${var.project_name}-*"
        ]
      },
      {
        Sid    = "S3ObjectAccess"
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:PutObjectAcl",
          "s3:GetObject",
          "s3:DeleteObject"
        ]
        Resource = [
          "arn:aws:s3:::${var.project_name}-*/*"
        ]
      },
      {
        Sid    = "S3NBADataAccess"
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:PutObjectAcl",
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::${var.nba_data_bucket_name}",
          "arn:aws:s3:::${var.nba_data_bucket_name}/*"
        ]
      }
    ]
  })

  tags = {
    Name      = "${var.project_name}-template-s3-management"
    ManagedBy = "terraform"
  }
}

# IAM Policy for DynamoDB Management (State Locking and Table Management)
# Consolidated: dynamodb_state_lock + dynamodb_management
resource "aws_iam_policy" "dynamodb_management" {
  name        = "${var.project_name}-template-dynamodb-management"
  description = "Permissions for DynamoDB state locking and table management"

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
      },
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
          "arn:aws:dynamodb:${var.aws_region}:*:table/${var.project_name}-*"
        ]
      }
    ]
  })

  tags = {
    Name      = "${var.project_name}-template-dynamodb-management"
    ManagedBy = "terraform"
  }
}

# IAM Policy for Additional AWS Services (EventBridge, SNS, SQS, API Gateway)
resource "aws_iam_policy" "additional_services" {
  name        = "${var.project_name}-template-additional-services"
  description = "Permissions for EventBridge, SNS, SQS, and API Gateway"

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
          "arn:aws:scheduler:${var.aws_region}:*:schedule/default/${var.project_name}-*"
        ]
      },
      {
        Sid    = "EventBridgeRulesManagement"
        Effect = "Allow"
        Action = [
          "events:PutRule",
          "events:DeleteRule",
          "events:DescribeRule",
          "events:ListRules",
          "events:EnableRule",
          "events:DisableRule",
          "events:PutTargets",
          "events:RemoveTargets",
          "events:ListTargetsByRule",
          "events:TagResource",
          "events:UntagResource",
          "events:ListTagsForResource"
        ]
        Resource = [
          "arn:aws:events:${var.aws_region}:*:rule/${var.project_name}-*"
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
          "sns:GetSubscriptionAttributes",
          "sns:ListSubscriptionsByTopic",
          "sns:ListTagsForResource",
          "sns:TagResource",
          "sns:UntagResource"
        ]
        Resource = [
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
      }
    ]
  })

  tags = {
    Name      = "${var.project_name}-template-additional-services"
    ManagedBy = "terraform"
  }
}

# IAM Policy for EC2 Infrastructure (EC2, VPC, Cognito, SSM)
# Consolidated: ec2_management + cognito_management + ssm_management
resource "aws_iam_policy" "ec2_infrastructure" {
  name        = "${var.project_name}-template-ec2-infrastructure"
  description = "Permissions for EC2, VPC, Cognito, and SSM for EC2-based services"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "EC2InstanceManagement"
        Effect = "Allow"
        Action = [
          "ec2:RunInstances",
          "ec2:TerminateInstances",
          "ec2:StartInstances",
          "ec2:StopInstances",
          "ec2:DescribeInstances",
          "ec2:DescribeInstanceStatus",
          "ec2:DescribeInstanceAttribute",
          "ec2:DescribeInstanceTypes",
          "ec2:DescribeInstanceCreditSpecifications",
          "ec2:ModifyInstanceAttribute",
          "ec2:GetConsoleOutput",
          "ec2:DescribeImages",
          "ec2:DescribeTags",
          "ec2:CreateTags",
          "ec2:DeleteTags"
        ]
        Resource = "*"
      },
      {
        Sid    = "EC2VPCManagement"
        Effect = "Allow"
        Action = [
          "ec2:CreateVpc",
          "ec2:DeleteVpc",
          "ec2:DescribeVpcs",
          "ec2:ModifyVpcAttribute",
          "ec2:DescribeVpcAttribute",
          "ec2:CreateSubnet",
          "ec2:DeleteSubnet",
          "ec2:DescribeSubnets",
          "ec2:ModifySubnetAttribute",
          "ec2:CreateInternetGateway",
          "ec2:DeleteInternetGateway",
          "ec2:AttachInternetGateway",
          "ec2:DetachInternetGateway",
          "ec2:DescribeInternetGateways",
          "ec2:CreateRouteTable",
          "ec2:DeleteRouteTable",
          "ec2:DescribeRouteTables",
          "ec2:CreateRoute",
          "ec2:DeleteRoute",
          "ec2:AssociateRouteTable",
          "ec2:DisassociateRouteTable",
          "ec2:CreateSecurityGroup",
          "ec2:DeleteSecurityGroup",
          "ec2:DescribeSecurityGroups",
          "ec2:AuthorizeSecurityGroupIngress",
          "ec2:RevokeSecurityGroupIngress",
          "ec2:AuthorizeSecurityGroupEgress",
          "ec2:RevokeSecurityGroupEgress",
          "ec2:DescribeSecurityGroupRules",
          "ec2:ModifySecurityGroupRules"
        ]
        Resource = "*"
      },
      {
        Sid    = "EC2EIPManagement"
        Effect = "Allow"
        Action = [
          "ec2:AllocateAddress",
          "ec2:ReleaseAddress",
          "ec2:AssociateAddress",
          "ec2:DisassociateAddress",
          "ec2:DescribeAddresses"
        ]
        Resource = "*"
      },
      {
        Sid    = "EC2VolumeManagement"
        Effect = "Allow"
        Action = [
          "ec2:DescribeVolumes",
          "ec2:DescribeVolumeStatus",
          "ec2:ModifyVolume"
        ]
        Resource = "*"
      },
      {
        Sid    = "EC2KeyPairAndAMI"
        Effect = "Allow"
        Action = [
          "ec2:DescribeKeyPairs",
          "ec2:DescribeAvailabilityZones"
        ]
        Resource = "*"
      },
      {
        Sid    = "CognitoUserPoolManagement"
        Effect = "Allow"
        Action = [
          "cognito-idp:CreateUserPool",
          "cognito-idp:DeleteUserPool",
          "cognito-idp:DescribeUserPool",
          "cognito-idp:UpdateUserPool",
          "cognito-idp:ListUserPools",
          "cognito-idp:ListTagsForResource",
          "cognito-idp:TagResource",
          "cognito-idp:UntagResource",
          "cognito-idp:CreateUserPoolClient",
          "cognito-idp:DeleteUserPoolClient",
          "cognito-idp:DescribeUserPoolClient",
          "cognito-idp:UpdateUserPoolClient",
          "cognito-idp:ListUserPoolClients",
          "cognito-idp:SetUserPoolMfaConfig",
          "cognito-idp:GetUserPoolMfaConfig"
        ]
        Resource = "arn:aws:cognito-idp:${var.aws_region}:*:userpool/*"
      },
      {
        Sid    = "SSMParameterManagement"
        Effect = "Allow"
        Action = [
          "ssm:PutParameter",
          "ssm:GetParameter",
          "ssm:GetParameters",
          "ssm:GetParametersByPath",
          "ssm:DeleteParameter",
          "ssm:ListTagsForResource",
          "ssm:AddTagsToResource",
          "ssm:RemoveTagsFromResource"
        ]
        Resource = [
          "arn:aws:ssm:${var.aws_region}:*:parameter/${var.project_name}*/*"
        ]
      },
      {
        Sid    = "SSMParameterDescribe"
        Effect = "Allow"
        Action = [
          "ssm:DescribeParameters"
        ]
        Resource = "*"
      },
      {
        Sid    = "SSMRunCommand"
        Effect = "Allow"
        Action = [
          "ssm:SendCommand",
          "ssm:GetCommandInvocation",
          "ssm:ListCommandInvocations",
          "ssm:DescribeInstanceInformation"
        ]
        Resource = [
          "arn:aws:ec2:${var.aws_region}:*:instance/*",
          "arn:aws:ssm:${var.aws_region}::document/AWS-RunShellScript"
        ]
      }
    ]
  })

  tags = {
    Name      = "${var.project_name}-template-ec2-infrastructure"
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

resource "aws_iam_role_policy_attachment" "cloudwatch_management" {
  role       = aws_iam_role.github_actions_pipeline.name
  policy_arn = aws_iam_policy.cloudwatch_management.arn
}

resource "aws_iam_role_policy_attachment" "s3_management" {
  role       = aws_iam_role.github_actions_pipeline.name
  policy_arn = aws_iam_policy.s3_management.arn
}

resource "aws_iam_role_policy_attachment" "dynamodb_management" {
  role       = aws_iam_role.github_actions_pipeline.name
  policy_arn = aws_iam_policy.dynamodb_management.arn
}

resource "aws_iam_role_policy_attachment" "additional_services" {
  role       = aws_iam_role.github_actions_pipeline.name
  policy_arn = aws_iam_policy.additional_services.arn
}

resource "aws_iam_role_policy_attachment" "ec2_infrastructure" {
  role       = aws_iam_role.github_actions_pipeline.name
  policy_arn = aws_iam_policy.ec2_infrastructure.arn
}
