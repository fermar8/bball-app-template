# Terraform Bootstrap

This directory contains the bootstrap configuration that sets up:
- S3 bucket for Terraform remote state
- DynamoDB table for state locking
- GitHub Actions OIDC provider
- IAM role `bball-app-template-pipeline-role` for GitHub Actions

## ⚠️ Important: Run This First

This bootstrap configuration must be deployed **before** the main resources, as it creates the backend infrastructure and pipeline role that other configurations depend on.

## Setup Steps

### 1. Configure Variables

Copy the example tfvars file:

```bash
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars`:

```hcl
state_bucket_name = "bball-app-terraform-state-123456789012"  # Use your AWS account ID
github_org        = "your-org"
github_repo       = "your-repo"
aws_region        = "eu-west-3"
```

**Note**: S3 bucket names must be globally unique. Include your AWS account ID or another unique identifier.

### 2. Deploy Bootstrap Resources

```bash
# Initialize Terraform (uses local state initially)
terraform init

# Review the plan
terraform plan

# Apply the configuration
terraform apply
```

### 3. Note the Outputs

After deployment, save these outputs:

```bash
# Pipeline role ARN (for GitHub Actions)
terraform output pipeline_role_arn

# State bucket name (for backend configuration)
terraform output state_bucket_name

# Lock table name (for backend configuration)
terraform output lock_table_name

# Get backend configuration template
terraform output backend_config
```

### 4. Migrate Bootstrap to Remote State (Optional)

After creating the S3 bucket and DynamoDB table, you can migrate this bootstrap configuration to use remote state:

Create `backend.tf`:

```hcl
terraform {
  backend "s3" {
    bucket         = "tfstate-590183661886-eu-west-3"
    key            = "bootstrap/terraform.tfstate"
    region         = "eu-west-3"
    dynamodb_table = "terraform-state-lock"
    encrypt        = true
  }
}
```

Then run:

```bash
terraform init -migrate-state
```

### 5. Configure GitHub Repository

In your GitHub repository settings, add these variables:

- `AWS_PIPELINE_ROLE_ARN`: The pipeline role ARN from outputs
- `AWS_REGION`: Your AWS region (e.g., `eu-west-3`)
- `TF_STATE_BUCKET`: The S3 bucket name from outputs
- `TF_LOCK_TABLE`: The DynamoDB table name from outputs

### 6. Update Resources Configuration

In your `terraform/resources` directory, create or update `backend.tf`:

```hcl
terraform {
  backend "s3" {
    bucket         = "tfstate-590183661886-eu-west-3"
    key            = "resources/terraform.tfstate"
    region         = "eu-west-3"
    dynamodb_table = "terraform-state-lock"
    encrypt        = true
  }
}
```

## What Gets Created

### S3 State Bucket
- **Purpose**: Store Terraform state files
- **Features**: 
  - Versioning enabled
  - Encryption at rest (AES256)
  - Public access blocked
  - Secure by default

### DynamoDB Lock Table
- **Purpose**: Prevent concurrent Terraform operations
- **Features**:
  - Pay-per-request billing
  - Hash key: `LockID`
  - Prevents state corruption

### GitHub OIDC Provider
- **Purpose**: Enables keyless authentication from GitHub Actions
- **Security**: No AWS access keys needed

### Pipeline IAM Role
- **Name**: `bball-app-template-pipeline-role`
- **Permissions**:
  - Lambda function management
  - IAM role management (for Lambda execution roles)
  - CloudWatch Logs management
  - S3 state access
  - DynamoDB state locking

## Security Features

✅ **No Access Keys**: Uses OIDC for GitHub Actions authentication  
✅ **Encrypted State**: S3 encryption and DynamoDB encryption at rest  
✅ **Versioned State**: S3 versioning prevents accidental deletions  
✅ **State Locking**: DynamoDB prevents concurrent modifications  
✅ **Least Privilege**: Role permissions scoped to specific resources  
✅ **Repository Scoped**: Role can only be assumed by your GitHub repo  

## Troubleshooting

### Bucket name already exists
S3 bucket names must be globally unique. Add your AWS account ID or a unique suffix:
```hcl
state_bucket_name = "bball-app-terraform-state-123456789012"
```

### OIDC provider already exists
If you already have a GitHub OIDC provider:
```hcl
create_oidc_provider       = false
existing_oidc_provider_arn = "arn:aws:iam::123456789012:oidc-provider/token.actions.githubusercontent.com"
```

### Role assumption fails
- Verify `github_org` and `github_repo` are correct
- Check repository name matches exactly (case-sensitive)
- Ensure workflow has `id-token: write` permission

## Cleanup

⚠️ **Warning**: Only destroy if you want to remove ALL state management infrastructure.

```bash
# This will destroy the state bucket, lock table, and pipeline role
terraform destroy
```

Before destroying:
1. Ensure no other projects are using this state bucket
2. Back up any important state files
3. Remove backend configurations from other projects
