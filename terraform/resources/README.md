# Basketball App Lambda Resources

This Terraform configuration deploys the bball-app Lambda function to AWS.

## Resources Created

- **Lambda Function**: `bball-app-template-{environment}`
- **IAM Role**: Execution role for the Lambda function
- **CloudWatch Log Group**: For Lambda logs with configurable retention
- **Lambda Package**: Automatically built from Go source code

## Environments

The function name is automatically suffixed based on the environment:
- `bball-app-template-nonlive` (for testing/development)
- `bball-app-template-live` (for production)

## Prerequisites

- Terraform >= 1.0
- Go 1.24+ installed
- AWS credentials configured
- AWS CLI (optional, for testing)

## Deployment

### 1. Configure Variables

Copy the example tfvars file:

```bash
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` and set the `environment` variable:

```hcl
environment = "nonlive"  # or "live"
```

### 2. Deploy

```bash
# Initialize Terraform
terraform init

# Review the plan
terraform plan

# Apply the configuration
terraform apply
```

### 3. Deploy Both Environments

To deploy both live and nonlive environments:

**Option A: Using separate tfvars files**

```bash
# Deploy nonlive
terraform apply -var-file=terraform.tfvars -var="environment=nonlive"

# Deploy live
terraform apply -var-file=terraform.tfvars -var="environment=live"
```

**Option B: Using workspaces**

```bash
# Create and deploy nonlive
terraform workspace new nonlive
terraform apply -var="environment=nonlive"

# Create and deploy live
terraform workspace new live
terraform apply -var="environment=live"
```

## Testing

After deployment, test the Lambda function:

```bash
# Get the function name from outputs
FUNCTION_NAME=$(terraform output -raw lambda_function_name)

# Invoke the function
aws lambda invoke \
  --function-name $FUNCTION_NAME \
  --payload '{}' \
  response.json

# View the response
cat response.json
```

## Outputs

After deployment, you'll get:

- `lambda_function_name`: Full function name (e.g., `bball-app-template-nonlive`)
- `lambda_function_arn`: ARN of the Lambda function
- `lambda_role_arn`: ARN of the execution role
- `lambda_log_group`: CloudWatch log group name
- `lambda_invoke_arn`: Invoke ARN (for API Gateway integration)

## Updating the Function

To update the Lambda code:

1. Make changes to the Go code in `cmd/lambda/` or `internal/handler/`
2. Run `terraform apply` - it will rebuild and redeploy automatically

## Clean Up

To remove all resources:

```bash
terraform destroy
```

## Configuration Options

| Variable | Description | Default |
|----------|-------------|---------|
| `aws_region` | AWS region | `eu-west-3` |
| `function_name` | Base function name | `bball-app-template` |
| `environment` | Environment (live/nonlive) | Required |
| `timeout` | Function timeout (seconds) | `30` |
| `memory_size` | Function memory (MB) | `128` |
| `log_retention_days` | Log retention period | `7` |

## Troubleshooting

### Build fails

Ensure Go is installed and `go.mod` is properly configured:

```bash
go mod download
go mod verify
```

### Permission errors

Ensure your AWS credentials have permissions to create:
- Lambda functions
- IAM roles and policies
- CloudWatch log groups

### Function invocation fails

Check the CloudWatch logs:

```bash
aws logs tail /aws/lambda/bball-app-template-nonlive --follow
```
