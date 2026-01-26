resource "aws_s3_bucket" "nba_data" {
  bucket = var.nba_data_bucket_name

  tags = {
    Name      = "bball-app-nba-data"
    ManagedBy = "terraform"
    Purpose   = "NBA API data storage"
  }
}

resource "aws_s3_bucket_versioning" "nba_data" {
  bucket = aws_s3_bucket.nba_data.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "nba_data" {
  bucket = aws_s3_bucket.nba_data.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Lifecycle policy to manage costs
resource "aws_s3_bucket_lifecycle_configuration" "nba_data" {
  bucket = aws_s3_bucket.nba_data.id

  rule {
    id     = "archive-old-data"
    status = "Enabled"

    filter {}

    transition {
      days          = 90
      storage_class = "STANDARD_IA"
    }

    transition {
      days          = 180
      storage_class = "GLACIER"
    }
  }
}
