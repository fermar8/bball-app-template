# Terraform Resources

This directory contains **per-project Lambda infrastructure** that gets deployed automatically via GitHub Actions pipeline.

## 📦 What Gets Deployed

- **Lambda Function**: Your application code => two are created, as per environment (nonlive/live)
- **DynamoDB Table**: Created per environment (nonlive/live)
- **IAM Role**: Lambda execution permissions
- **CloudWatch Logs**: Function logging
- **SQS Dead Letter Queue (Live only)**: Stores failed events so they can be replayed later

## ⚙️ How It Works

The pipeline deploys these resources and **automatically references bootstrap infrastructure**:

```
┌─────────────────────────────────────┐
│  GitHub Actions Pipeline            │
│  (Triggered on push)                │
└──────────────┬──────────────────────┘
               │
               ├─ Uses IAM role from bootstrap
               ├─ Reads bootstrap state from S3
               │
               ↓
┌─────────────────────────────────────┐
│  Resources (this directory)         │
│  ┌───────────────────────────────┐  │
│  │ Lambda Function               │  │
│  │ DynamoDB Table (per env)      │  │
│  │ IAM Role & Policies           │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
               │
               │ References via remote state
               ↓
┌─────────────────────────────────────┐
│  Bootstrap (deployed once)          │
│  - S3 state bucket                  │
│  - DynamoDB state lock              │
│  - GitHub Actions IAM role          │
│  - OIDC provider                    │
└─────────────────────────────────────┘
```

---

## 🔗 Referencing Bootstrap Resources

### 1. Backend Configuration

The `backend.tf` file tells Terraform where to store state:

```hcl
terraform {
  backend "s3" {
    bucket         = "tfstate-590183661886-eu-west-3"
    key            = "resources/nonlive/bball-app-template.tfstate"
    region         = "eu-west-3"
    dynamodb_table = "terraform-state-lock"
    encrypt        = true
  }
}
```

**Key points:**
- `bucket` - The S3 bucket created by bootstrap
- `key` - Unique path per environment: `resources/{env}/{project}.tfstate`
- `dynamodb_table` - Lock table created by bootstrap

### 2. Data Source Configuration

The `data.tf` file reads bootstrap outputs:

```hcl
data "terraform_remote_state" "bootstrap" {
  backend = "s3"
  
  config = {
    bucket = var.bootstrap_state_bucket
    key    = "bootstrap/roles-and-db-config.tfstate"  # Must match bootstrap backend.tf
    region = var.aws_region
  }
}
```

**What this does:**
- Reads bootstrap Terraform state from S3
- Makes bootstrap outputs available: `data.terraform_remote_state.bootstrap.outputs.pipeline_role_arn`
- No hardcoded ARNs needed - everything is dynamic

### 3. Using Bootstrap Outputs

In `lambda.tf`, resources reference bootstrap:

```hcl
# Example: Using bootstrap outputs (if you had them)
resource "aws_lambda_function" "function" {
  # Your Lambda configuration
  
  environment {
    variables = {
      DYNAMODB_TABLE_NAME = aws_dynamodb_table.app_table.name
      # Could reference bootstrap outputs here if needed:
      # SHARED_RESOURCE = data.terraform_remote_state.bootstrap.outputs.some_value
    }
  }
}
```

**Current setup:**
- DynamoDB tables are created **in resources** (per environment)
- Lambda gets table name from the locally-created table
- Bootstrap provides: state bucket, lock table, IAM role for pipeline

---

## 🚀 Deployment Process

### Automatic (via Pipeline)

**Push to GitHub** → Pipeline runs automatically:

```bash
git add .
git commit -m "Update Lambda code"
git push origin main  # or develop
```

**Pipeline does:**
1. ✅ Authenticates via OIDC (no access keys)
2. ✅ Assumes IAM role from bootstrap
3. ✅ Initializes Terraform with remote backend
4. ✅ Creates/updates Lambda + DynamoDB table
5. ✅ Deploys to `nonlive` environment (from develop) or `live` (from main)

**GitHub secrets required:**
```
AWS_PIPELINE_ROLE_ARN = arn:aws:iam::590183661886:role/bball-app-template-pipeline-role
AWS_REGION            = eu-west-3
TF_STATE_BUCKET       = tfstate-590183661886-eu-west-3
TF_LOCK_TABLE         = terraform-state-lock
```

---

## 📝 Variables Configuration

### Required Variables

In `variables.tf`, these variables need values:

| Variable | Description | Set By |
|----------|-------------|--------|
| `bootstrap_state_bucket` | S3 bucket with bootstrap state | Pipeline (from GitHub secret) |
| `environment` | Deployment environment (`nonlive` or `live`) | Pipeline (from branch) |
| `aws_region` | AWS region | Pipeline (from GitHub secret) |
| `function_name` | Lambda function base name | `variables.tf` default |

### Example Variable Usage

```hcl
# variables.tf
variable "bootstrap_state_bucket" {
  description = "S3 bucket containing bootstrap state"
  type        = string
  # Set by pipeline: -var="bootstrap_state_bucket=${TF_STATE_BUCKET}"
  # Value: "tfstate-590183661886-eu-west-3" (same bucket as bootstrap)
}

variable "environment" {
  description = "Environment (nonlive or live)"
  type        = string
  # Set by pipeline: -var="environment=nonlive"
}

variable "function_name" {
  description = "Lambda function base name"
  type        = string
  default     = "bball-app-template"
  # Can override in terraform.tfvars if needed
}
```

**Important:** `bootstrap_state_bucket` is the **same S3 bucket** where bootstrap stores its state:
- Bucket name: `tfstate-590183661886-eu-west-3`

---

## 🛠️ Troubleshooting

### Pipeline Error: "Resources can't find bootstrap outputs"

**Problem:** `data.tf` has wrong state key.

**Solution:** Ensure `data.tf` has correct key matching bootstrap:

```hcl
data "terraform_remote_state" "bootstrap" {
  backend = "s3"
  config = {
    bucket = var.bootstrap_state_bucket
    key    = "bootstrap/roles-and-db-config.tfstate"  # Must match bootstrap backend.tf
    region = var.aws_region
  }
}
```

### Pipeline Error: "State lock timeout"

**Problem:** Previous pipeline run was interrupted, leaving a lock.

**Solution:** Clear the lock in AWS Console:
1. Go to DynamoDB → `terraform-state-lock` table (eu-west-3)
2. Find item with key `resources/nonlive/bball-app-template.tfstate` (or live)
3. Delete the lock item
4. Re-run the pipeline

### Pipeline Error: "Access Denied"

**Problem:** IAM role permissions or GitHub OIDC setup.

**Solution:**
1. ✅ Verify GitHub secrets are set correctly
2. ✅ Check bootstrap IAM role exists: `bball-app-template-pipeline-role`
3. ✅ Verify workflow has `permissions: id-token: write`
4. ✅ Check role trust policy allows your GitHub repo

### Error: "DynamoDB table already exists"

**Problem:** Table exists from previous deployment, but not in Terraform state.

**Solution:** Import existing table:
```bash
terraform import aws_dynamodb_table.app_table bball-app-template-nonlive
terraform apply
```

---

## 🎯 Adding New Resources

To add EventBridge, API Gateway, or other resources:

### 1. Create New Terraform File

```bash
# terraform/resources/api_gateway.tf
resource "aws_apigatewayv2_api" "lambda_api" {
  name          = "${var.function_name}-${var.environment}-api"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_integration" "lambda" {
  api_id           = aws_apigatewayv2_api.lambda_api.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.function.invoke_arn
}
```

### 2. Push to GitHub

Pipeline automatically deploys the new resources! ✅

---

## 📚 File Structure

```
terraform/resources/
├── backend.tf           # Where to store Terraform state
├── data.tf              # Reference bootstrap outputs
├── variables.tf         # Input variables
├── lambda.tf            # Lambda function configuration
├── dynamodb.tf          # DynamoDB table (per environment)
├── sqs-dlq.tf            # Dead Letter Queue (live only)
├── event-bridge-event-rule-scheduler.tf  # Scheduled trigger (optional)
├── outputs.tf           # Export values for other tools
├── terraform.tfvars     # Variable values (optional, for local testing)
└── README.md            # This file
```

---

## 🎓 Key Concepts

### Remote State

Terraform stores its state in S3 (not locally):
- ✅ Shared across team members and CI/CD
- ✅ Locked via DynamoDB (prevents conflicts)
- ✅ Versioned (can recover from mistakes)
- ✅ Encrypted

### Data Sources

The `data` blocks read information without creating resources:
- `data "terraform_remote_state" "bootstrap"` - Reads bootstrap outputs
- Outputs become available as `data.terraform_remote_state.bootstrap.outputs.xxx`

### Per-Environment Resources

Resources are created separately for each environment:
- **Nonlive**: DynamoDB table `bball-app-template-nonlive`, Lambda `bball-app-template-nonlive`
- **Live**: DynamoDB table `bball-app-template-live`, Lambda `bball-app-template-live`
- State stored in different S3 keys: `resources/nonlive/...` vs `resources/live/...`

---

## 📖 Next Steps

1. ✅ Bootstrap deployed → Done (ran once locally)
2. ✅ Resources configured → You're here
3. 🚀 Push to GitHub → Pipeline deploys Lambda + DynamoDB
4. 📊 Monitor in AWS Console → CloudWatch logs, DynamoDB tables
5. 🎯 Add more resources → API Gateway, EventBridge, etc.
