
resource "aws_cloudwatch_event_rule" "lambda_schedule" {
  name                = "${var.function_name}-schedule-${var.environment}"
  description         = "Trigger Lambda function on a schedule"
  schedule_expression = var.scheduler_expression
  state               = var.scheduler_enabled ? "ENABLED" : "DISABLED"

  tags = merge(var.tags, { Environment = var.environment })
}

# Target: connect the rule to the Lambda function
resource "aws_cloudwatch_event_target" "lambda_target" {
  rule      = aws_cloudwatch_event_rule.lambda_schedule.name
  target_id = "LambdaTarget"
  arn       = aws_lambda_function.function.arn

  input = jsonencode({
    action = "create",
    data: {
    name: "Test Entry",
    value: 42
  }
  })
}

# Lambda permission to allow EventBridge to invoke it
resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.function.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.lambda_schedule.arn
}

