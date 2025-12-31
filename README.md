# Basketball App Template - Python Lambda

A Python-based AWS Lambda function template for the basketball app.

## Structure

```
├── src/
│   └── handler.py          # Lambda function handler
├── tests/
│   └── test_handler.py     # Unit tests
├── terraform/
│   ├── bootstrap/          # Infrastructure setup
│   ├── resources/          # Lambda deployment
│   └── roles/              # (deprecated)
├── .github/
│   └── workflows/          # CI/CD pipelines
├── requirements.txt        # Production dependencies
└── requirements-dev.txt    # Development dependencies
```

## Local Development

### Prerequisites

- Python 3.12+
- AWS CLI configured
- Terraform >= 1.0

### Setup

```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate.bat  # On Windows (PowerShell has execution policy restrictions)

# Install dependencies
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt
```

### Running Tests

```bash
# Run all tests with coverage
python -m pytest tests/ -v --cov=src --cov-report=term-missing

# Run specific test
python -m pytest tests/test_handler.py::TestHandler::test_lambda_handler_success -v
```

### Local Testing

```python
from src.handler import lambda_handler

event = {"test": "data"}
context = {}
response = lambda_handler(event, context)
print(response)
```

## Deployment

### Automated (via GitHub Actions)

**Branch deployments** (nonlive environment):
- Push to any branch triggers build, test, and plan
- Does not deploy automatically

**Main deployments** (nonlive → live):
1. Push to `main` branch
2. Deploys to nonlive automatically
3. Waits for approval
4. Deploys to live after approval
5. Creates GitHub release

### Manual (local)

```powershell
cd terraform/resources

# Deploy to nonlive
terraform init -backend-config="backend.hcl"
terraform plan -var="environment=nonlive"
terraform apply -var="environment=nonlive"

# Deploy to live
terraform plan -var="environment=live"
terraform apply -var="environment=live"
```

## Lambda Configuration

- **Runtime**: Python 3.12
- **Handler**: `handler.lambda_handler`
- **Memory**: 128 MB (configurable)
- **Timeout**: 30 seconds (configurable)
- **Environment Variables**:
  - `ENVIRONMENT`: `live` or `nonlive`

## Adding Dependencies

1. Add to `requirements.txt`:
   ```
   boto3==1.34.0
   requests==2.31.0
   ```

2. Install locally:
   ```powershell
   python -m pip install -r requirements.txt
   ```

3. Lambda will automatically package dependencies on deployment

## Testing the Deployed Function

```powershell
# Invoke the function
aws lambda invoke `
  --function-name bball-app-template-nonlive `
  --payload '{"test": "data"}' `
  response.json

# View response
Get-Content response.json

# View logs
aws logs tail /aws/lambda/bball-app-template-nonlive --follow
```

## CI/CD Workflows

### branches.yml
- Triggers on push to any branch (except main)
- Runs tests and terraform plan
- Does not deploy

### main.yml
- Triggers on push to main
- Deploys to nonlive automatically
- Requires approval for live deployment
- Creates GitHub release with artifacts

## Infrastructure

### Bootstrap (one-time setup)
```powershell
cd terraform/bootstrap
terraform init
terraform apply
```

Creates:
- S3 bucket for state
- DynamoDB table for locking
- IAM role for GitHub Actions
- OIDC provider

### Resources (Lambda functions)
Managed via workflows or locally:
- `bball-app-template-nonlive`
- `bball-app-template-live`

## Environment Configuration

Set these GitHub repository variables:
- `AWS_PIPELINE_ROLE_ARN`: Pipeline IAM role ARN
- `AWS_REGION`: AWS region (default: eu-west-3)
- `TF_STATE_BUCKET`: S3 state bucket name
- `TF_LOCK_TABLE`: DynamoDB lock table name

## License

See LICENSE file.
