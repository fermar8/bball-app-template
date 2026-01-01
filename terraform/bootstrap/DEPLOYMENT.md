# Bootstrap Infrastructure - Deployment Guide

## Overview

This directory contains **shared infrastructure** deployed **once** and used by multiple Lambda projects.

## What's Deployed

### Shared Infrastructure
- **VPC and Networking**: VPC, public/private subnets, NAT Gateway, Internet Gateway, route tables
- **RDS PostgreSQL**: Single database instance shared across all Lambda projects
- **Security Groups**: Shared Lambda and RDS security groups
- **Secrets Manager**: Database credentials

### CI/CD Infrastructure
- **S3 Bucket**: Terraform state storage with encryption and versioning
- **DynamoDB Table**: State locking
- **GitHub OIDC**: Authentication for GitHub Actions
- **IAM Role**: Pipeline role for deployments

## Architecture

```
┌─────────────────────────────────────────────────┐
│              VPC (10.0.0.0/16)                 │
│                                                 │
│  ┌──────────────┐  ┌────────────────────────┐ │
│  │   Public     │  │  Private (Lambda)      │ │
│  │   Subnets    │  │  10.0.11.x/24          │ │
│  │ NAT Gateway  │  │  Multiple Lambdas →    │ │
│  └──────────────┘  └────────────────────────┘ │
│                                                 │
│                    ┌────────────────────────┐ │
│                    │  Private (RDS)         │ │
│                    │  10.0.1.x/24           │ │
│                    │  PostgreSQL RDS ←      │ │
│                    └────────────────────────┘ │
└─────────────────────────────────────────────────┘

Multiple Lambda Projects → Same Database
```

## Deployment Order

### Step 1: Configure Variables

```bash
cd terraform/bootstrap
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars`:

```hcl
# Required
state_bucket_name = "bball-app-tfstate-123456789012"  # Must be globally unique
github_org        = "your-github-org"
github_repo       = "your-repo-name"

# Optional (has defaults)
project_name      = "bball-app"
aws_region        = "eu-west-3"
vpc_cidr          = "10.0.0.0/16"
db_instance_class = "db.t3.micro"
```

### Step 2: Deploy Bootstrap

```bash
terraform init
terraform plan
terraform apply
```

### Step 3: Save Important Outputs

```bash
# State bucket (needed for Lambda projects)
terraform output state_bucket_name

# Database connection (for reference)
terraform output db_endpoint

# Secrets ARN (for Lambda environment)
terraform output db_secret_arn

# Pipeline role (for GitHub Actions)
terraform output pipeline_role_arn
```

### Step 4: Deploy Lambda Projects

After bootstrap completes, deploy individual Lambda functions in `terraform/resources/`.

Each Lambda project will reference bootstrap outputs via remote state.

## Key Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `state_bucket_name` | S3 bucket for Terraform state (must be globally unique) | **Required** |
| `github_org` | GitHub organization or username | **Required** |
| `github_repo` | GitHub repository name | **Required** |
| `project_name` | Prefix for resource names | `bball-app` |
| `aws_region` | AWS region | `eu-west-3` |
| `vpc_cidr` | VPC CIDR block | `10.0.0.0/16` |
| `db_instance_class` | RDS instance type | `db.t3.micro` |
| `db_allocated_storage` | Initial DB storage (GB) | `20` |
| `db_name` | Database name | `bball_app` |
| `db_username` | Database master username | `dbadmin` |

## Outputs (Used by Lambda Projects)

Bootstrap provides these outputs for Lambda projects to consume:

```hcl
# Networking
vpc_id                    # VPC identifier
private_lambda_subnet_ids # Subnets for Lambda functions
lambda_security_group_id  # Security group for Lambdas

# Database
db_endpoint   # Full database endpoint (host:port)
db_address    # Database host only
db_name       # Database name
db_username   # Database master username
db_secret_arn # ARN of Secrets Manager secret with credentials
db_port       # Database port (5432)

# CI/CD
state_bucket_name  # S3 bucket for Terraform state
pipeline_role_arn  # IAM role for GitHub Actions
```

## Cost Estimate

Monthly costs for shared infrastructure:

| Resource | Estimated Cost |
|----------|----------------|
| NAT Gateway | ~$32/month |
| RDS db.t3.micro | ~$15/month |
| S3 + DynamoDB | ~$1/month |
| **Total** | **~$48/month** |

> **Tip**: For development, you can stop the RDS instance when not in use to save costs.

## Multi-Project Usage

This bootstrap infrastructure supports multiple Lambda projects:

```
terraform/bootstrap/      ← Deploy once (VPC, RDS, shared resources)
    ↓
terraform/resources/      ← Lambda Project A (references bootstrap)
    ↓
other-project/terraform/  ← Lambda Project B (references same bootstrap)
    ↓
another-project/terraform ← Lambda Project C (references same bootstrap)
```

All projects share:
- Same VPC and networking
- Same RDS PostgreSQL instance
- Same database (different tables/schemas if needed)
- Different Lambda functions with separate code

## Troubleshooting

### Bucket name already exists
S3 bucket names must be globally unique. Add your AWS account ID or random suffix.

### OIDC provider already exists
If you've deployed GitHub OIDC before:
```hcl
create_oidc_provider     = false
existing_oidc_provider_arn = "arn:aws:iam::ACCOUNT_ID:oidc-provider/token.actions.githubusercontent.com"
```

### RDS takes too long
Initial RDS deployment can take 10-15 minutes. This is normal.

## Security Notes

- Database password is auto-generated (32 characters with special chars)
- Password stored in AWS Secrets Manager
- Deletion protection enabled on RDS for production safety
- VPC has private subnets for database isolation
- Security groups restrict RDS access to Lambda only

## Next Steps

1. ✅ Deploy bootstrap infrastructure (you're here)
2. → Deploy Lambda function in `terraform/resources/`
3. → Test database connectivity
4. → Deploy additional Lambda projects as needed
