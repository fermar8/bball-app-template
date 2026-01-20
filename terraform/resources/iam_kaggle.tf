# IAM Policy for Lambda to read Kaggle credentials from Secrets Manager
resource "aws_iam_policy" "lambda_kaggle_secrets" {
  name        = "${var.function_name}-${var.environment}-kaggle-secrets-policy"
  description = "Allow Lambda to read Kaggle credentials from Secrets Manager"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "ReadKaggleSecret"
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = [
          "arn:aws:secretsmanager:${var.aws_region}:*:secret:${var.kaggle_secret_name}-*"
        ]
      }
    ]
  })

  tags = merge(var.tags, { Environment = var.environment })
}

# IAM Policy for Lambda to upload Kaggle datasets to S3
resource "aws_iam_policy" "lambda_kaggle_s3" {
  name        = "${var.function_name}-${var.environment}-kaggle-s3-policy"
  description = "Allow Lambda to upload Kaggle datasets to S3"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "PutKaggleDatasets"
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:AbortMultipartUpload"
        ]
        Resource = [
          "arn:aws:s3:::${var.s3_data_bucket}/${var.s3_prefix}/*"
        ]
      },
      {
        Sid    = "ListKaggleBucket"
        Effect = "Allow"
        Action = [
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::${var.s3_data_bucket}"
        ]
      }
    ]
  })

  tags = merge(var.tags, { Environment = var.environment })
}

# Attach Secrets Manager policy to Lambda role
resource "aws_iam_role_policy_attachment" "lambda_kaggle_secrets" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_kaggle_secrets.arn
}

# Attach S3 policy to Lambda role
resource "aws_iam_role_policy_attachment" "lambda_kaggle_s3" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_kaggle_s3.arn
}
