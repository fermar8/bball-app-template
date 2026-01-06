# Purpose: trigger the Lambda on a schedule.
# Safety: disabled by default in live via live.tfvars

# IAM role assumed by EventBridge Scheduler to invoke the Lambda target
resource "aws_iam_role" "scheduler_invoke_role" {
  name = "${var.function_name}-${var.environment}-scheduler-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "scheduler.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })

  tags = merge(var.tags, { Environment = var.environment })
}

# Policy allowing the scheduler role to invoke the Lambda
resource "aws_iam_policy" "scheduler_invoke_lambda" {
  name        = "${var.function_name}-${var.environment}-scheduler-invoke-lambda"
  description = "Allow EventBridge Scheduler to invoke the Lambda"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = ["lambda:InvokeFunction"]
      Resource = [
        aws_lambda_function.function.arn,
        "${aws_lambda_function.function.arn}:*"
      ]
    }]
  })

  tags = merge(var.tags, { Environment = var.environment })
}

resource "aws_iam_role_policy_attachment" "scheduler_invoke_lambda" {
  role       = aws_iam_role.scheduler_invoke_role.name
  policy_arn = aws_iam_policy.scheduler_invoke_lambda.arn
}

# The schedule itself (created in both envs, but disabled live by default)
resource "aws_scheduler_schedule" "lambda_schedule" {
  name                = "${var.function_name}-${var.environment}-schedule"
  schedule_expression = var.scheduler_expression

  state = var.scheduler_enabled ? "ENABLED" : "DISABLED"

  flexible_time_window {
    mode = "OFF"
  }

  target {
    arn      = aws_lambda_function.function.arn
    role_arn = aws_iam_role.scheduler_invoke_role.arn

    input = jsonencode({
      action = "create"
    })
  }

}
