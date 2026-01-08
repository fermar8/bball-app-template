# SNS Topic for CloudWatch Alarms
resource "aws_sns_topic" "lambda_alarms" {
  count = var.environment == "live" ? 1 : 0
  name  = "${var.project_name}-${var.environment}-lambda-alarms"

  tags = merge(var.tags, { 
    Environment = var.environment
    Purpose     = "Lambda error notifications"
  })
}

# CloudWatch Alarm - Lambda Errors
resource "aws_cloudwatch_metric_alarm" "lambda_errors" {
  count               = var.environment == "live" ? 1 : 0
  alarm_name          = "${var.function_name}-${var.environment}-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = 60
  statistic           = "Sum"
  threshold           = 0
  alarm_description   = "Triggers when Lambda function has errors"
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = aws_lambda_function.function.function_name
  }

  alarm_actions = [aws_sns_topic.lambda_alarms[0].arn]
  ok_actions    = [aws_sns_topic.lambda_alarms[0].arn]

  tags = merge(var.tags, { 
    Environment = var.environment
  })
}

# Email subscriptions for alarms
resource "aws_sns_topic_subscription" "lambda_alarms_email" {
  for_each  = var.environment == "live" ? toset(var.alarm_emails) : []
  topic_arn = aws_sns_topic.lambda_alarms[0].arn
  protocol  = "email"
  endpoint  = each.value
}

# Output SNS topic ARN for email subscription
output "lambda_alarms_topic_arn" {
  description = "SNS topic ARN for Lambda alarms - subscribe your email to receive notifications"
  value       = var.environment == "live" ? aws_sns_topic.lambda_alarms[0].arn : null
}
