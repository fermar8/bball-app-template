resource "aws_sqs_queue" "lambda_deadletter" {
  count = var.environment == "live" ? 1 : 0

  name = "bball-app-template-deadletter"

  # 3 days
  message_retention_seconds = 259200

  tags = merge(var.tags, { Environment = var.environment })
}
