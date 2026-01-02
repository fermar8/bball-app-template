# Terraform Bootstrap

This directory contains the bootstrap configuration that sets up the **foundation infrastructure** for your serverless application. This should be deployed **once** and shared across all our Lambda projects.

## 🏗️ What Gets Created

### State Management
- **S3 Bucket**: Stores Terraform state files for all projects
- **DynamoDB Table**: Provides state locking to prevent concurrent modifications

### CI/CD Pipeline Authentication
- **GitHub OIDC Provider**: Enables keyless authentication from GitHub Actions
- **Pipeline IAM Role**: `bball-app-template-pipeline-role` with permissions to deploy Lambda functions and DynamoDB tables

### State Location
- **State Key**: `bootstrap/roles-and-db-config.tfstate`

---

## ⚠️ Important: Run This First

Deploy bootstrap **before** running any pipelines or deploying resources. The bootstrap creates:
1. The backend (S3 + DynamoDB) where Terraform stores state
2. The IAM role that GitHub Actions uses to deploy resources

**📌 After Configuration Changes**: If you modified the backend state key in `backend.tf`, you must redeploy bootstrap before running the pipeline:

```bash
cd terraform/bootstrap
terraform init -reconfigure  # Updates backend to new state key
terraform apply              # Redeploys with new configuration
```

---

## 📋 Setup Steps

### 1. Configure Variables

Edit `terraform.tfvars` with our values:

```hcl
state_bucket_name = "tfstate-590183661886-eu-west-3"
github_org        = "fermar8"                         
github_repo       = "bball-app-template"              
aws_region        = "eu-west-3"                       
```

**💡 Tip**: Use `tfstate-{AWS_ACCOUNT_ID}-{REGION}` format for globally unique bucket names.

---

### 2. Deploy Bootstrap (Local, One-Time)

```bash
# Initialize Terraform
terraform init

# If backend configuration changed (state key update), use:
terraform init -reconfigure

# Review what will be created
terraform plan

# Apply the configuration
terraform apply
```

---

### 3. Save Important Outputs

After deployment, save these values:

```bash
# View all outputs
terraform output

# Copy these for GitHub Actions configuration
terraform output pipeline_role_arn    # For GitHub secret
terraform output state_bucket_name    # For resources backend config
terraform output lock_table_name      # For resources backend config
```

---

### 4. Configure GitHub Repository Secrets

Add these to your GitHub repository (Settings → Secrets and variables → Actions):

**Secrets/Variables:**
```
AWS_PIPELINE_ROLE_ARN = <output from pipeline_role_arn>
AWS_REGION            = eu-west-3
TF_STATE_BUCKET       = <output from state_bucket_name>
TF_LOCK_TABLE         = <output from lock_table_name>
```

---

### 5. Bootstrap State is Automatically Remote

The bootstrap creates the S3 bucket and DynamoDB table, then **Terraform automatically uses them** because of the `backend.tf` configuration:

```hcl
terraform {
  backend "s3" {
    bucket         = "tfstate-590183661886-eu-west-3"
    key            = "bootstrap/roles-and-db-config.tfstate"
    region         = "eu-west-3"
    dynamodb_table = "terraform-state-lock"
    encrypt        = true
  }
}
```

**How it works:**
1. First `terraform init` - Backend doesn't exist yet, uses local state temporarily
2. `terraform apply` - Creates S3 bucket + DynamoDB table
3. Terraform automatically migrates local state → S3 after resources are created
4. Future operations use remote state from S3

**Result:** Bootstrap state is safely stored in S3, not on your local machine.

---

### 6. You're Done! 🎉

Bootstrap is complete. Now you can:
- ✅ Deploy Lambda functions via GitHub Actions pipeline
- ✅ Create multiple Lambda projects that share this bootstrap
- ✅ Add EventBridge, API Gateway, etc. in the resources layer

**Before running the pipeline**, ensure:
1. ✅ Bootstrap has been applied successfully
2. ✅ GitHub secrets are configured
3. ✅ Resources `data.tf` references the correct state key: `bootstrap/roles-and-db-config.tfstate`

---

## 🔐 Security Features

✅ **No Access Keys**: Uses OIDC for passwordless GitHub Actions authentication  
✅ **Encrypted State**: S3 encryption (AES256) and DynamoDB encryption at rest  
✅ **Versioned State**: S3 versioning prevents accidental state deletions  
✅ **State Locking**: DynamoDB prevents concurrent Terraform operations  
✅ **Least Privilege**: IAM role permissions scoped to specific actions  
✅ **Repository Scoped**: Role can only be assumed by your specific GitHub repo  

---

## 🎯 What Belongs in Bootstrap vs Resources

### ✅ Bootstrap (Deploy Once, Shared)
- State backend (S3 + DynamoDB)
- GitHub OIDC provider
- Pipeline IAM roles

### ❌ Resources (Deploy Per Project/Environment via Pipeline)
- Lambda functions
- DynamoDB tables (app-specific, created per environment)
- EventBridge Scheduler
- API Gateway
- CloudWatch rules
- SNS/SQS queues

**Rule of thumb**: If it costs money when idle or is shared across projects → Bootstrap. If it's pay-per-use and project-specific → Resources.

---

## 🛠️ Troubleshooting

### Bucket name already exists
S3 bucket names must be globally unique across ALL AWS accounts:

```hcl
state_bucket_name = "tfstate-590183661886-eu-west-3"  # Include account ID
```

### OIDC provider already exists
If you already created a GitHub OIDC provider in your AWS account:

```hcl
create_oidc_provider       = false
existing_oidc_provider_arn = "arn:aws:iam::590183661886:oidc-provider/token.actions.githubusercontent.com"
```

### Resources already exist (after changing state key)
If you changed the backend state key and see "already exists" errors:

```bash
# Import existing resources into new state location
terraform import aws_s3_bucket.terraform_state tfstate-590183661886-eu-west-3
terraform import aws_dynamodb_table.terraform_locks terraform-state-lock
terraform import 'aws_iam_openid_connect_provider.github[0]' 'arn:aws:iam::590183661886:oidc-provider/token.actions.githubusercontent.com'
terraform import aws_iam_role.github_actions_pipeline bball-app-template-pipeline-role
# ... import remaining policies
terraform apply  # Creates any missing resources
```

### Backend configuration changed
If you see "Backend configuration changed" errors after modifying `backend.tf`:

```bash
terraform init -reconfigure  # Reconfigure backend with new settings
```

---

## 🧹 Cleanup

⚠️ **Warning**: Only destroy if you want to remove ALL infrastructure for ALL projects.

```bash
terraform destroy
```

**Before destroying:**
1. ✅ Destroy all resources in `terraform/resources` first
2. ✅ Ensure no other projects use this state bucket
3. ✅ Back up important state files from S3
4. ✅ Remove GitHub secrets/variables


