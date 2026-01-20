# EventBridge Rule for Kaggle dataset ingestion
resource "aws_cloudwatch_event_rule" "kaggle_schedule" {
  count               = var.kaggle_enabled ? 1 : 0
  name                = "${var.function_name}-kaggle-schedule-${var.environment}"
  description         = "Trigger Lambda function for Kaggle dataset ingestion"
  schedule_expression = var.kaggle_schedule_expression
  state               = "ENABLED"

  tags = merge(var.tags, { Environment = var.environment })
}

# Target: connect the Kaggle rule to the Lambda function
resource "aws_cloudwatch_event_target" "kaggle_target" {
  count     = var.kaggle_enabled ? 1 : 0
  rule      = aws_cloudwatch_event_rule.kaggle_schedule[0].name
  target_id = "KaggleIngestTarget"
  arn       = aws_lambda_function.function.arn

  # Pass job identifier to Lambda handler for routing
  input = jsonencode({
    job = "kaggle_ingest"
  })

  # Retry policy for EventBridge -> Lambda deliveries (live environment)
  dynamic "retry_policy" {
    for_each = var.environment == "live" ? [1] : []
    content {
      maximum_event_age_in_seconds = 60
      maximum_retry_attempts       = 0
    }
  }
}

# Lambda permission to allow EventBridge (Kaggle rule) to invoke it
resource "aws_lambda_permission" "allow_eventbridge_kaggle" {
  count         = var.kaggle_enabled ? 1 : 0
  statement_id  = "AllowExecutionFromEventBridgeKaggle"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.function.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.kaggle_schedule[0].arn
}
