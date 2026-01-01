# Lambda Resources - Deployment Guide

## Overview

This directory contains **per-project Lambda infrastructure** that references the shared bootstrap infrastructure.

## What's Deployed

- AWS Lambda function
- IAM role and policies for Lambda execution
- CloudWatch log group
- Lambda VPC configuration (connects to shared network)

## Prerequisites

**IMPORTANT**: Bootstrap infrastructure must be deployed first!

```bash
cd terraform/bootstrap
terraform apply  # Deploy once
cd ../resources  # Then come here
```

## Architecture

```
┌──────────────────────────────────────────────┐
│  Lambda Project (this directory)            │
│  ┌────────────────────────────────────────┐ │
│  │  Lambda Function                       │ │
│  │  - Reads from shared RDS               │ │
│  │  - Uses shared VPC/subnets             │ │
│  │  - Uses shared security groups         │ │
│  └────────────────────────────────────────┘ │
└──────────────────────────────────────────────┘
         │
         ├─ References bootstrap via remote state
         │
         ↓
┌──────────────────────────────────────────────┐
│  Bootstrap (terraform/bootstrap/)           │
│  - VPC & Networking                         │
│  - RDS PostgreSQL                           │
│  - Security Groups                          │
│  - Secrets Manager                          │
└──────────────────────────────────────────────┘
```

## Deployment Steps

### Step 1: Configure Variables

```bash
cd terraform/resources
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars`:

```hcl
# Required: Must match bootstrap state bucket
bootstrap_state_bucket = "bball-app-tfstate-123456789012"

# Lambda configuration
function_name = "bball-app-template"
environment   = "nonlive"  # or "live"
aws_region    = "eu-west-3"

# Lambda settings
timeout     = 30
memory_size = 128
```

**Critical**: `bootstrap_state_bucket` must match the bucket from bootstrap deployment.

### Step 2: Initialize Backend

```bash
# Create backend.hcl if it doesn't exist
cat > backend.hcl << EOF
bucket         = "bball-app-tfstate-123456789012"  # Same as bootstrap
key            = "resources/terraform.tfstate"
region         = "eu-west-3"
dynamodb_table = "bball-app-terraform-locks"
encrypt        = true
EOF

# Initialize with backend config
terraform init -backend-config=backend.hcl
```

### Step 3: Deploy Lambda

```bash
terraform plan
terraform apply
```

### Step 4: Test Lambda

```bash
# Get function name
FUNCTION_NAME=$(terraform output -raw lambda_function_name)

# Test invocation
aws lambda invoke \
  --function-name $FUNCTION_NAME \
  --payload '{"action":"create","data":{"name":"test","value":42}}' \
  response.json

cat response.json
```

## How It Works

### Remote State Reference

This configuration reads bootstrap outputs via remote state:

```hcl
data "terraform_remote_state" "bootstrap" {
  backend = "s3"
  config = {
    bucket = var.bootstrap_state_bucket  # From your tfvars
    key    = "bootstrap/terraform.tfstate"
    region = var.aws_region
  }
}
```

### Bootstrap Resources Used

Lambda function automatically gets:

```hcl
# VPC Configuration
subnet_ids = data.terraform_remote_state.bootstrap.outputs.private_lambda_subnet_ids
security_group_ids = [data.terraform_remote_state.bootstrap.outputs.lambda_security_group_id]

# Database Connection
DB_SECRET_ARN = data.terraform_remote_state.bootstrap.outputs.db_secret_arn
DB_HOST       = data.terraform_remote_state.bootstrap.outputs.db_address
DB_PORT       = data.terraform_remote_state.bootstrap.outputs.db_port
DB_NAME       = data.terraform_remote_state.bootstrap.outputs.db_name
```

## Environment Variables

Lambda receives these environment variables automatically:

| Variable | Source | Example |
|----------|--------|---------|
| `ENVIRONMENT` | Your tfvars | `nonlive` or `live` |
| `DB_SECRET_ARN` | Bootstrap output | `arn:aws:secretsmanager:...` |
| `DB_HOST` | Bootstrap output | `bball-app-db.xxxxx.eu-west-3.rds.amazonaws.com` |
| `DB_PORT` | Bootstrap output | `5432` |
| `DB_NAME` | Bootstrap output | `bball_app` |
| `DB_USER` | Bootstrap output | `dbadmin` |
| `DB_MIN_CONNECTIONS` | Hard-coded | `1` |
| `DB_MAX_CONNECTIONS` | Hard-coded | `5` |

## Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `bootstrap_state_bucket` | S3 bucket with bootstrap state | ✅ Yes | - |
| `function_name` | Lambda function name (without env suffix) | No | `bball-app-template` |
| `environment` | Deployment environment (`live` or `nonlive`) | ✅ Yes | - |
| `aws_region` | AWS region | No | `eu-west-3` |
| `timeout` | Lambda timeout (seconds) | No | `30` |
| `memory_size` | Lambda memory (MB) | No | `128` |
| `log_retention_days` | CloudWatch log retention | No | `7` |

## Outputs

```bash
# View all outputs
terraform output

# Specific outputs
terraform output lambda_function_name  # bball-app-template-nonlive
terraform output lambda_function_arn   # arn:aws:lambda:...
terraform output db_endpoint           # From bootstrap
```

## Multiple Environments

Deploy the same Lambda to different environments:

**Nonlive (Dev/Test)**
```hcl
# terraform.tfvars
environment = "nonlive"
```

**Live (Production)**
```hcl
# terraform-live.tfvars
environment = "live"
timeout     = 60
memory_size = 256
```

Deploy:
```bash
# Nonlive
terraform apply

# Live (separate workspace)
terraform workspace new live
terraform apply -var-file=terraform-live.tfvars
```

## Cost Estimate

Per Lambda project (excluding shared infrastructure):

| Resource | Estimated Cost |
|----------|----------------|
| Lambda execution (1M requests/month) | ~$0.20 |
| CloudWatch Logs (10 GB/month) | ~$0.50 |
| **Total** | **~$0.70/month** |

> Shared infrastructure (VPC, RDS) costs are in bootstrap (~$48/month).

## CI/CD Integration

GitHub Actions workflows automatically deploy this infrastructure:

```yaml
# .github/workflows/main.yml already configured
- name: Terraform Init
  run: terraform init -backend-config=backend.hcl

- name: Terraform Apply
  run: terraform apply -auto-approve
```

## Troubleshooting

### Error: "bucket does not exist"

**Problem**: `bootstrap_state_bucket` is incorrect or bootstrap not deployed.

**Solution**: 
```bash
cd terraform/bootstrap
terraform output state_bucket_name  # Get correct bucket name
cd ../resources
# Update bootstrap_state_bucket in terraform.tfvars
```

### Error: "no outputs found"

**Problem**: Bootstrap state doesn't have outputs.

**Solution**: Ensure bootstrap is deployed:
```bash
cd terraform/bootstrap
terraform apply
```

### Lambda can't connect to database

**Problem**: VPC configuration or security groups.

**Solution**:
1. Check Lambda is in correct subnets (from bootstrap)
2. Check security group allows Lambda → RDS traffic
3. Verify RDS endpoint in bootstrap outputs

### Deploy fails with "InvalidParameterValueException"

**Problem**: Subnet or security group IDs don't exist.

**Solution**: Verify bootstrap is deployed and outputs are correct:
```bash
cd terraform/bootstrap
terraform output vpc_id
terraform output private_lambda_subnet_ids
terraform output lambda_security_group_id
```

## Adding More Lambda Projects

To add another Lambda project using the same database:

1. Copy this `resources/` directory to new project
2. Update `function_name` in new project's `terraform.tfvars`
3. Update Lambda source code path in `lambda.tf`
4. Keep same `bootstrap_state_bucket` to reuse infrastructure
5. Deploy: `terraform init -backend-config=backend.hcl && terraform apply`

Example:
```bash
# New project structure
other-lambda-project/
  src/              # Different Lambda code
  terraform/
    backend.hcl     # Same bootstrap bucket reference
    terraform.tfvars  # Different function_name
    lambda.tf       # Points to different src/
```

Both Lambda functions will:
- Share same VPC
- Share same RDS database
- Have separate IAM roles and logs
- Be independently deployable

## Next Steps

1. ✅ Deploy Lambda (you're here)
2. → Test database connectivity
3. → Set up API Gateway (if needed)
4. → Deploy additional Lambda projects
5. → Monitor via CloudWatch
