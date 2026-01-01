# Terraform Infrastructure - Overview

## Architecture: Bootstrap + Resources Pattern

This project uses a **two-tier Terraform architecture** that separates shared infrastructure from per-project resources.

```
terraform/
├── bootstrap/        ← Deploy ONCE (shared infrastructure)
│   ├── main.tf
│   ├── database.tf   ← VPC, RDS, networking
│   ├── backend.tf
│   └── DEPLOYMENT.md ← Start here
│
└── resources/        ← Deploy PER PROJECT (Lambda functions)
    ├── main.tf
    ├── lambda.tf     ← Lambda function only
    ├── data.tf       ← References bootstrap outputs
    └── DEPLOYMENT.md ← Then here
```

## Why This Pattern?

### Problem
- Multiple Lambda projects need the same database
- VPC and networking are expensive (NAT Gateway ~$32/month)
- RDS should be shared, not duplicated per project

### Solution
**Bootstrap** (deploy once):
- VPC with public/private subnets
- RDS PostgreSQL instance
- NAT Gateway
- Shared security groups
- CI/CD infrastructure (S3, DynamoDB, IAM)

**Resources** (deploy per Lambda):
- Lambda function code
- Lambda-specific IAM roles
- CloudWatch logs
- References bootstrap via remote state

### Benefits
✅ **Cost Efficient**: Single VPC and RDS for all projects (~$48/month instead of $48 × N)  
✅ **Data Sharing**: All Lambdas access same database  
✅ **Independent Deployments**: Each Lambda deploys separately  
✅ **Easy Scaling**: Add new Lambdas without recreating infrastructure  

## Quick Start

### 1️⃣ Deploy Bootstrap (Once)

```bash
cd terraform/bootstrap
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values
terraform init
terraform apply

# Save this output!
terraform output state_bucket_name
```

**Time**: ~15 minutes (RDS creation is slow)  
**Frequency**: Once per AWS account/region  

See [bootstrap/DEPLOYMENT.md](bootstrap/DEPLOYMENT.md) for details.

### 2️⃣ Deploy Lambda Project (Per Project)

```bash
cd terraform/resources
cp terraform.tfvars.example terraform.tfvars
# Edit: Set bootstrap_state_bucket from step 1
terraform init -backend-config=backend.hcl
terraform apply
```

**Time**: ~2 minutes  
**Frequency**: Once per Lambda function  

See [resources/DEPLOYMENT.md](resources/DEPLOYMENT.md) for details.

## What Gets Deployed

### Bootstrap Infrastructure (Shared)

| Resource | Purpose | Monthly Cost |
|----------|---------|--------------|
| VPC | Network isolation | Free |
| NAT Gateway | Lambda internet access | ~$32 |
| RDS PostgreSQL | Shared database | ~$15 |
| Security Groups | Network security | Free |
| Secrets Manager | DB credentials | ~$0.40 |
| S3 + DynamoDB | Terraform state | ~$1 |
| **Total** | | **~$48/month** |

### Lambda Resources (Per Project)

| Resource | Purpose | Monthly Cost |
|----------|---------|--------------|
| Lambda Function | Application code | ~$0.20 |
| IAM Role | Permissions | Free |
| CloudWatch Logs | Logging | ~$0.50 |
| **Total** | | **~$0.70/month** |

**Example**: 3 Lambda projects = $48 (bootstrap) + 3 × $0.70 = **$50.10/month**

## Remote State Flow

```
┌─────────────────────────────────────────────┐
│  Lambda Project A (resources/)             │
│  Reads: bootstrap outputs via S3           │
│  Gets: VPC ID, subnets, DB endpoint, etc.  │
└─────────────────────────────────────────────┘
         ↓ (S3 remote state)
┌─────────────────────────────────────────────┐
│  Bootstrap (bootstrap/)                    │
│  Outputs: vpc_id, db_endpoint, etc.        │
│  State: s3://bucket/bootstrap/tfstate      │
└─────────────────────────────────────────────┘
         ↓ (Creates actual resources)
┌─────────────────────────────────────────────┐
│  AWS Resources                             │
│  - VPC (10.0.0.0/16)                       │
│  - RDS (bball-app-db)                      │
│  - Lambda Functions                        │
└─────────────────────────────────────────────┘
```

Lambda projects reference bootstrap like this:

```hcl
# In resources/data.tf
data "terraform_remote_state" "bootstrap" {
  backend = "s3"
  config = {
    bucket = var.bootstrap_state_bucket  # User provides this
    key    = "bootstrap/terraform.tfstate"
    region = var.aws_region
  }
}

# In resources/lambda.tf
vpc_config {
  subnet_ids = data.terraform_remote_state.bootstrap.outputs.private_lambda_subnet_ids
  # ... uses bootstrap outputs
}
```

## Multi-Project Example

Deploy multiple Lambda functions sharing the same database:

```bash
# Step 1: Deploy shared infrastructure (once)
cd terraform/bootstrap/
terraform apply  # Creates VPC, RDS, networking

# Step 2: Deploy Lambda Project A
cd ../resources/
terraform workspace new project-a
terraform apply  # Lambda A → same database

# Step 3: Deploy Lambda Project B (in different repo/folder)
cd ../../other-project/terraform/
terraform init -backend-config=backend.hcl
terraform apply  # Lambda B → same database

# Step 4: Deploy Lambda Project C
cd ../../another-project/terraform/
terraform apply  # Lambda C → same database
```

All three Lambdas:
- ✅ Use same VPC (10.0.0.0/16)
- ✅ Connect to same RDS instance
- ✅ Share security groups
- ✅ Have independent IAM roles
- ✅ Deploy independently

## Directory Structure

```
bball-app-template/
├── src/                          # Lambda source code
│   ├── messaging/handler.py      # Lambda entry point
│   ├── service/service.py        # Business logic
│   ├── repository/repository.py  # Database access
│   └── database/database.py      # Connection pool
│
├── tests/
│   ├── unit/                     # Fast tests (mocked)
│   └── integration/              # Real DB tests
│
├── terraform/
│   ├── bootstrap/               ← Deploy first
│   │   ├── DEPLOYMENT.md        # Detailed guide
│   │   ├── main.tf              # Provider config
│   │   ├── database.tf          # VPC, RDS, networking
│   │   ├── backend.tf           # S3, DynamoDB, GitHub OIDC
│   │   ├── variables.tf         # Input variables
│   │   ├── outputs.tf           # Exported values
│   │   └── terraform.tfvars.example
│   │
│   └── resources/               ← Deploy per Lambda
│       ├── DEPLOYMENT.md        # Detailed guide
│       ├── main.tf              # Provider config
│       ├── lambda.tf            # Lambda function
│       ├── data.tf              # Bootstrap remote state
│       ├── variables.tf         # Input variables
│       ├── outputs.tf           # Lambda outputs
│       └── terraform.tfvars.example
│
└── .github/workflows/
    ├── branches.yml             # CI for feature branches
    └── main.yml                 # CD for main branch
```

## Deployment Workflow

### Initial Setup (First Time)

```bash
# 1. Deploy bootstrap
cd terraform/bootstrap
terraform init
terraform apply
# Note: state_bucket_name = "bball-app-tfstate-123456"

# 2. Deploy first Lambda
cd ../resources
# Edit terraform.tfvars: bootstrap_state_bucket = "bball-app-tfstate-123456"
terraform init -backend-config=backend.hcl
terraform apply
```

### Adding New Lambda Project

```bash
# 1. Create new project (copy this template)
cp -r bball-app-template new-lambda-project

# 2. Update code
cd new-lambda-project/src/
# ... modify Lambda code ...

# 3. Deploy Lambda (reuse same bootstrap)
cd terraform/resources
# Edit terraform.tfvars:
#   bootstrap_state_bucket = "bball-app-tfstate-123456"  (same as before!)
#   function_name = "new-lambda-project"                  (different name)
terraform init -backend-config=backend.hcl
terraform apply
```

### Updating Shared Infrastructure

```bash
# Modify bootstrap (affects all Lambdas)
cd terraform/bootstrap
# Edit database.tf (e.g., increase RDS instance size)
terraform plan   # See impact on shared resources
terraform apply  # All Lambdas will use new infrastructure
```

### Updating Individual Lambda

```bash
# Modify Lambda code or configuration
cd src/
# ... edit code ...

cd terraform/resources
terraform apply  # Only affects this Lambda
```

## State Management

### Bootstrap State
- **Location**: S3 bucket created by bootstrap itself
- **Key**: `bootstrap/terraform.tfstate`
- **Shared By**: All Lambda projects (read-only reference)

### Lambda State
- **Location**: Same S3 bucket as bootstrap
- **Key**: `resources/terraform.tfstate` (or per-project key)
- **Shared By**: Single Lambda project only

### State File Layout in S3

```
s3://bball-app-tfstate-123456/
├── bootstrap/
│   └── terraform.tfstate        ← Shared infrastructure
│
├── resources/
│   └── terraform.tfstate        ← Lambda Project A
│
├── project-b/
│   └── terraform.tfstate        ← Lambda Project B
│
└── project-c/
    └── terraform.tfstate        ← Lambda Project C
```

## When to Use This Pattern

✅ **Good Fit**:
- Multiple Lambda functions need same database
- Want to minimize infrastructure costs
- Need shared networking/VPC
- Deploying microservices with shared data layer

❌ **Not Ideal**:
- Single Lambda function (just use resources/ directly)
- Completely isolated environments (separate VPCs needed)
- Different databases per Lambda

## Environment Strategy

### Option A: Separate Bootstraps per Environment

```bash
# Bootstrap for Dev
cd terraform/bootstrap
terraform workspace new dev
terraform apply  # Creates dev-vpc, dev-rds

# Bootstrap for Prod
terraform workspace new prod
terraform apply  # Creates prod-vpc, prod-rds

# Lambda in Dev
cd ../resources
terraform workspace new dev
terraform apply -var="environment=nonlive"

# Lambda in Prod
terraform workspace new prod
terraform apply -var="environment=live"
```

### Option B: Single Bootstrap, Multiple Lambda Environments

```bash
# One bootstrap (shared dev/prod)
cd terraform/bootstrap
terraform apply

# Lambda for Dev
cd ../resources
terraform apply -var="environment=nonlive"

# Lambda for Prod (separate workspace or directory)
terraform workspace new prod
terraform apply -var="environment=live"
```

**Recommendation**: Use **Option A** for production (separate VPCs for isolation).

## Security Considerations

### Bootstrap
- ✅ RDS in private subnets (no public access)
- ✅ Database password auto-generated and stored in Secrets Manager
- ✅ Deletion protection enabled on RDS
- ✅ Encryption at rest for RDS and S3
- ✅ Security groups restrict RDS to Lambda only

### Lambda Resources
- ✅ IAM role with least privilege
- ✅ Secrets Manager access only for DB credentials
- ✅ VPC execution role for network access
- ✅ CloudWatch logs for audit trail

## Troubleshooting

### Bootstrap Issues

**Problem**: S3 bucket name already exists  
**Solution**: Bucket names are globally unique. Add AWS account ID or random suffix.

**Problem**: RDS takes too long (>10 minutes)  
**Solution**: This is normal. RDS creation is slow.

### Resources Issues

**Problem**: "Error: no outputs found in bootstrap state"  
**Solution**: Deploy bootstrap first: `cd terraform/bootstrap && terraform apply`

**Problem**: Lambda can't connect to database  
**Solution**: Check security groups allow Lambda → RDS on port 5432

**Problem**: "InvalidParameterValueException: Subnet not found"  
**Solution**: Bootstrap not deployed or outputs incorrect

## Cost Optimization

### Development
- **Stop RDS when not in use**: Can save ~$15/month
- **Use db.t3.micro**: Smallest instance for development
- **Reduce log retention**: 1 day instead of 7

### Production
- **Reserved Instances**: Save 30-40% on RDS
- **NAT Gateway alternatives**: VPC endpoints for AWS services (avoid NAT)
- **Lambda reserved concurrency**: If predictable traffic

## Next Steps

1. ✅ Read this overview
2. → Follow [bootstrap/DEPLOYMENT.md](bootstrap/DEPLOYMENT.md) to deploy shared infrastructure
3. → Follow [resources/DEPLOYMENT.md](resources/DEPLOYMENT.md) to deploy Lambda
4. → Test database connectivity
5. → Add more Lambda projects as needed

## Additional Resources

- [AWS VPC Best Practices](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-best-practices.html)
- [Terraform Remote State](https://www.terraform.io/language/state/remote)
- [AWS Lambda VPC Networking](https://docs.aws.amazon.com/lambda/latest/dg/configuration-vpc.html)
- [RDS PostgreSQL](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_PostgreSQL.html)
