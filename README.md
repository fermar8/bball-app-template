# Basketball App Template - Python Lambda

A serverless Python template project for AWS Lambda with DynamoDB, designed for rapid deployment using GitHub Actions OIDC authentication. This template includes a complete bootstrap infrastructure setup and automated CI/CD pipelines.

## Project Overview

This is a **template project** that demonstrates:
- **Layered Architecture**: Handler → Service → Repository → Model
- **DynamoDB Integration**: Serverless NoSQL database with pay-per-request billing
- **JSON Schema Validation**: Request validation at the handler layer
- **Infrastructure as Code**: Terraform with separated bootstrap and resources
- **GitHub Actions OIDC**: Secure deployments without AWS access keys

## Folder Structure

```
├── src/
│   ├── messaging/          # Handler and Lambda entry point
│   │   └── schemas/        # JSON schemas for event validation
│   ├── service/            # Business logic layer (no validation)
│   ├── repository/         # Data access layer (DynamoDB operations)
│   ├── model/              # Data models
│   └── database/           # DynamoDB connection management
├── tests/
│   ├── unit/               # Unit tests with mocked dependencies
│   └── integration/        # Integration tests with moto (DynamoDB mocking)
├── terraform/
│   ├── bootstrap/          # One-time infrastructure (roles, S3, OIDC)
│   └── resources/          # Per-environment resources (Lambda, DynamoDB)
├── .github/
│   └── workflows/          # CI/CD pipelines
├── requirements.txt        # Production dependencies (boto3, jsonschema)
├── requirements-dev.txt    # Development dependencies (pytest, moto)
└── pyproject.toml          # Python project configuration
```

## Running Tests Locally

### Prerequisites

- Python 3.12+
- Virtual environment

### Setup

```bash
# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate  # On Windows
source venv/bin/activate  # On Linux/Mac

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Run Tests

**Unit Tests** (fast, no external dependencies):
```bash
# Run all unit tests
poe test

# Run with coverage report
poe test-cov
```

**Integration Tests** (uses moto to mock DynamoDB):
```bash
# Run integration tests
poe test-integration

# Run all tests (unit + integration)
poe test-all
```

**Note**: Integration tests use [moto](https://github.com/getmoto/moto) to mock AWS DynamoDB, so they run locally without AWS credentials or a real database. They work on all platforms (Windows, Linux, Mac).

### Test Structure

- **Unit Tests**: Mock all dependencies, test individual components
  - `test_handler.py` - Tests JSON schema validation and routing
  - `test_service.py` - Tests business logic (no validation)
  - `test_models.py` - Tests data models
  
- **Integration Tests**: Use moto to mock DynamoDB, test full stack
  - `test_dynamodb_integration.py` - Tests Repository and Service with mocked DynamoDB

## Bootstrap Configuration

This template uses a **two-layer infrastructure approach**:

1. **Bootstrap** (`terraform/bootstrap/`) - Deploy **once** locally
   - Creates S3 bucket for Terraform state
   - Creates DynamoDB table for state locking
   - Creates GitHub OIDC provider and IAM role
   - See [terraform/bootstrap/README.md](terraform/bootstrap/README.md)

2. **Resources** (`terraform/resources/`) - Deploy via **pipeline** per environment
   - Creates Lambda function
   - Creates DynamoDB table (per environment)
   - References bootstrap via remote state
   - See [terraform/resources/README.md](terraform/resources/README.md)

## CI/CD Deployment

The project includes automated GitHub Actions workflows:

- **branches.yml**: Runs on feature branches - builds, tests, and plans (no deployment)
- **main.yml**: Runs on main branch - deploys to nonlive, then live (with approval)

All tests run automatically in the pipeline with no database setup required (moto handles DynamoDB mocking).

## License

See LICENSE file.
