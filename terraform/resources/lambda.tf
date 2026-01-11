# Lambda package without dependencies (layers will be used for dependencies)
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../../src"
  output_path = "${path.module}/lambda.zip"
}

# IAM role for Lambda
resource "aws_iam_role" "lambda_role" {
  name = "${var.function_name}-${var.environment}-role"

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

  tags = merge(
    var.tags,
    {
      Environment = var.environment
    }
  )
}

# Attach basic Lambda execution policy
resource "aws_iam_role_policy_attachment" "lambda_basic" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  role       = aws_iam_role.lambda_role.name
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/${var.function_name}-${var.environment}"
  retention_in_days = var.log_retention_days

  tags = merge(
    var.tags,
    {
      Environment = var.environment
    }
  )
}

# Lambda Function
resource "aws_lambda_function" "function" {
  filename         = data.archive_file.lambda_zip.output_path
  function_name    = "${var.function_name}-${var.environment}"
  role            = aws_iam_role.lambda_role.arn
  handler         = "src.messaging.handler.lambda_handler"
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  runtime         = "python3.12"
  timeout         = var.timeout
  memory_size     = var.memory_size

  dynamic "dead_letter_config" {
    for_each = var.environment == "live" ? [1] : []
    content {
      target_arn = aws_sqs_queue.lambda_deadletter[0].arn
    }
  }

  environment {
    variables = {
      ENVIRONMENT         = var.environment
      DYNAMODB_TABLE_NAME = aws_dynamodb_table.app_table.name
    }
  }

  tags = merge(
    var.tags,
    {
      Environment = var.environment
    }
  )

  depends_on = [
    aws_cloudwatch_log_group.lambda_logs,
    aws_iam_role_policy_attachment.lambda_basic,
    aws_iam_role_policy_attachment.lambda_dynamodb,
    aws_iam_role_policy_attachment.lambda_dlq
  ]
}

# Allow Lambda service to send failed async invocation events to the DLQ (LIVE only)
resource "aws_iam_policy" "lambda_dlq" {
  count       = var.environment == "live" ? 1 : 0
  name        = "${var.function_name}-${var.environment}-lambda-dlq-policy"
  description = "Allow Lambda to send failed events to SQS DLQ"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "sqs:SendMessage"
        ]
        Resource = aws_sqs_queue.lambda_deadletter[0].arn
      }
    ]
  })

  tags = merge(var.tags, { Environment = var.environment })
}

resource "aws_iam_role_policy_attachment" "lambda_dlq" {
  count      = var.environment == "live" ? 1 : 0
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_dlq[0].arn
}

# IAM Policy for Lambda to access DynamoDB
resource "aws_iam_policy" "lambda_dynamodb" {
  name        = "${var.function_name}-${var.environment}-lambda-dynamodb-policy"
  description = "Allow Lambda to access DynamoDB table"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:Query",
          "dynamodb:Scan"
        ]
        Resource = [
          aws_dynamodb_table.app_table.arn,
          "${aws_dynamodb_table.app_table.arn}/index/*"
        ]
      }
    ]
  })

  tags = merge(
    var.tags,
    {
      Environment = var.environment
    }
  )
}

# Attach DynamoDB policy to Lambda role
resource "aws_iam_role_policy_attachment" "lambda_dynamodb" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_dynamodb.arn
}

# IAM Policy for Lambda to read from DLQ (for replay mechanism)
resource "aws_iam_policy" "lambda_read_dlq" {
  count       = var.environment == "live" ? 1 : 0
  name        = "${var.function_name}-${var.environment}-read-dlq-policy"
  description = "Allow Lambda to read messages from SQS DLQ for replay"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes"
        ]
        Resource = aws_sqs_queue.lambda_deadletter[0].arn
      }
    ]
  })

  tags = merge(var.tags, { Environment = var.environment })
}

resource "aws_iam_role_policy_attachment" "lambda_read_dlq" {
  count      = var.environment == "live" ? 1 : 0
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_read_dlq[0].arn
}

# Event Source Mapping: DLQ processor (enabled for testing and replay)
resource "aws_lambda_event_source_mapping" "dlq_processor" {
  count            = var.environment == "live" ? 1 : 0
  event_source_arn = aws_sqs_queue.lambda_deadletter[0].arn
  function_name    = aws_lambda_function.function.arn
  batch_size       = 1
  enabled          = true
  
  # Retry attempts when processing messages from DLQ
  function_response_types = ["ReportBatchItemFailures"]
  
  # Maximum number of times to retry failed messages from DLQ
  # After this, messages stay in DLQ for manual inspection
  maximum_retry_attempts = 2

  depends_on = [
    aws_iam_role_policy_attachment.lambda_read_dlq
  ]
}
