# Basketball App Template - Python Lambda

A Python-based AWS Lambda function template for the basketball app.

## Structure

```
├── src/
│   ├── messaging/          # Handler and Lambda entry point
│   ├── service/            # Business logic layer
│   ├── repository/         # Data access layer
│   ├── model/              # Data models
│   └── database/           # Database connection management
├── tests/
│   ├── unit/               # Unit tests (fast, mocked)
│   └── integration/        # Integration tests (require database)
├── scripts/
│   ├── run_integration_tests.bat  # Windows integration test runner
│   └── run_integration_tests.sh   # Linux/WSL integration test runner
├── terraform/
│   ├── bootstrap/          # Infrastructure setup
│   └── resources/          # Lambda and RDS deployment
├── .github/
│   └── workflows/          # CI/CD pipelines
├── docker-compose.yml      # Local PostgreSQL for testing
├── pyproject.toml          # Python project configuration and test scripts
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
venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Running Tests

```bash
# Run unit tests (fast, works on all platforms)
poe test

# Run unit tests with coverage report
poe test-cov

# Run all tests (requires database - see below)
poe test-all
```

#### Integration Tests

Integration tests require a PostgreSQL database.

**✅ In CI/CD (GitHub Actions):**
- Automatically runs on Ubuntu with PostgreSQL service
- No setup needed - works out of the box

**⚠️ Locally on Windows:**
Due to a known issue with psycopg3 + Windows + Spanish locale PostgreSQL error messages, integration tests cannot run directly on Windows. 

**Options for local integration testing:**

1. **Use WSL2 (Recommended)**:
   ```bash
   # In WSL2
   ./scripts/run_integration_tests.sh
   ```

2. **Skip locally, run in CI/CD**:
   ```powershell
   # Just run unit tests locally
   poe test
   
   # Push to GitHub - integration tests run automatically
   git push
   ```

3. **Docker + WSL**:
   - Install WSL2 and Docker Desktop
   - Run integration tests in Linux environment

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
- **Handler**: `messaging.handler.lambda_handler`
- **Memory**: 128 MB (configurable)
- **Timeout**: 30 seconds (configurable)
- **Architecture**: Layered (Messaging → Service → Repository → Database)
- **Database**: PostgreSQL (AWS RDS)
- **Environment Variables**:
  - `ENVIRONMENT`: `live` or `nonlive`
  - `DB_HOST`: RDS endpoint
  - `DB_PORT`: `5432`
  - `DB_NAME`: Database name
  -psycopg[binary,pool]>=3.1.0
   boto3==1.34.162
   ```

2. Install locally:
   ```powershell
   pip install -r requirements.txt
   ```

3. Lambda will automatically package dependencies on deployment

## Available Commands (via poethepoet)

```bash
poe test                    # Run unit tests
poe test-unit              # Run unit tests (verbose)
poe test-integration       # Run integration tests (requires PostgreSQL)
poe test-all               # Run all tests
poe test-cov               # Run tests with HTML coverage report
```
- Unit tests use mocks (no database needed)
- Integration tests use Docker PostgreSQL (see above)

**Production:**
- AWS RDS PostgreSQL 15.5
- Deployed in private subnets
- Credentials stored in AWS Secrets Manager
- Connection pooling for performance

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
