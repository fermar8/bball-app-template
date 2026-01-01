# DynamoDB Table for Non-Live Environment
resource "aws_dynamodb_table" "nonlive" {
  name           = "bball-app-template-nonlive"
  billing_mode   = "PAY_PER_REQUEST"  # Pay only for what you use
  hash_key       = "id"

  attribute {
    name = "id"
    type = "S"  # String
  }

  # Global Secondary Index for querying by name (optional, for your use case)
  global_secondary_index {
    name            = "NameIndex"
    hash_key        = "name"
    projection_type = "ALL"
  }

  attribute {
    name = "name"
    type = "S"
  }

  # Point-in-time recovery
  point_in_time_recovery {
    enabled = false  # Disabled for dev to save costs
  }

  # Server-side encryption
  server_side_encryption {
    enabled = true
  }

  tags = merge(
    var.tags,
    {
      Name        = "bball-app-template-nonlive"
      Environment = "nonlive"
    }
  )
}

# DynamoDB Table for Live Environment
resource "aws_dynamodb_table" "live" {
  name           = "bball-app-template-live"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "id"

  attribute {
    name = "id"
    type = "S"
  }

  # Global Secondary Index for querying by name
  global_secondary_index {
    name            = "NameIndex"
    hash_key        = "name"
    projection_type = "ALL"
  }

  attribute {
    name = "name"
    type = "S"
  }

  # Point-in-time recovery for production
  point_in_time_recovery {
    enabled = true  # Enabled for live environment
  }

  # Server-side encryption
  server_side_encryption {
    enabled = true
  }

  tags = merge(
    var.tags,
    {
      Name        = "bball-app-template-live"
      Environment = "live"
    }
  )
}
