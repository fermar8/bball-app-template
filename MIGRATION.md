# Migration from Go to Python - Summary

## What Was Changed

### 1. **Python Lambda Code** ✅
- Created [src/handler.py](src/handler.py) - Main Lambda handler function
- Created [tests/test_handler.py](tests/test_handler.py) - Unit tests using pytest
- Created [requirements.txt](requirements.txt) - Production dependencies (currently empty)
- Created [requirements-dev.txt](requirements-dev.txt) - Testing dependencies (pytest, pytest-cov)

### 2. **Terraform Configuration** ✅
Updated [terraform/resources/main.tf](terraform/resources/main.tf):
- Changed `runtime` from `provided.al2023` (Go custom runtime) → `python3.12`
- Changed `handler` from `bootstrap` → `handler.lambda_handler`
- Changed archive source from single bootstrap binary → entire `src/` directory
- Terraform will now package all Python files in src/ directory

### 3. **GitHub Workflows** ✅
Updated [.github/workflows/branches.yml](.github/workflows/branches.yml):
- Replaced Go 1.24 setup with Python 3.12
- Replaced `go test` with `pytest`
- Removed Go binary build steps
- Added Python handler verification

Updated [.github/workflows/main.yml](.github/workflows/main.yml):
- Same Python setup as branches workflow
- Changed artifact from `lambda-bootstrap` → `lambda-package`
- Packages entire `src/` directory + dependencies
- Updated release notes to mention Python 3.12

### 4. **Documentation** ✅
Updated [README.md](README.md):
- Complete rewrite for Python development
- Added virtual environment setup
- Updated testing commands (pytest)
- Added dependency management guide
- Updated Lambda configuration details

## What to Delete (Old Go Files)

You can safely delete these Go-related files:

```
cmd/
  lambda/
    main.go          # Old Go Lambda entry point
internal/
  handler/
    handler.go       # Old Go handler
    handler_test.go  # Old Go tests
go.mod               # Go module definition
go.sum               # Go dependencies
main.go              # Old root main file (if exists)
main_test.go         # Old root tests (if exists)
```

## Next Steps

### 1. **Install Python Dependencies Locally**
```powershell
# Create virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 2. **Run Tests Locally**
```powershell
pytest tests/ -v --cov=src --cov-report=term-missing
```

Expected output:
```
tests/test_handler.py::TestHandler::test_lambda_handler_success PASSED
tests/test_handler.py::TestHandler::test_lambda_handler_empty_event PASSED

---------- coverage: platform win32, python 3.12 -----------
Name              Stmts   Miss  Cover   Missing
-----------------------------------------------
src/handler.py       10      0   100%
-----------------------------------------------
TOTAL                10      0   100%
```

### 3. **Update Terraform State (IMPORTANT!)**

Since the Lambda configuration changed (runtime, handler), you'll need to update both environments:

**For nonlive:**
```powershell
cd terraform/resources
terraform init -backend-config=backend.hcl
terraform plan -var="environment=nonlive"
# Review the plan - it will recreate the Lambda function
terraform apply -var="environment=nonlive"
```

**For live:**
```powershell
terraform plan -var="environment=live"
# Review the plan - it will recreate the Lambda function
terraform apply -var="environment=live"
```

### 4. **Test via GitHub Actions**

**Option A: Test on a branch first**
```powershell
git checkout -b test-python-migration
git add .
git commit -m "Migrate from Go to Python"
git push origin test-python-migration
```

This will trigger [.github/workflows/branches.yml](.github/workflows/branches.yml):
- Run Python tests
- Create Terraform plan (shows what will change)
- **Does NOT deploy** automatically

**Option B: Deploy to main**
```powershell
git checkout main
git merge test-python-migration
git push origin main
```

This will trigger [.github/workflows/main.yml](.github/workflows/main.yml):
1. Run tests
2. Deploy to nonlive automatically
3. Wait for your approval
4. Deploy to live after approval
5. Create GitHub release

### 5. **Test the Deployed Function**

```powershell
# Invoke nonlive function
aws lambda invoke `
  --function-name bball-app-template-nonlive `
  --payload '{\"test\": \"data\"}' `
  response.json

# View response
Get-Content response.json

# Expected response:
# {"statusCode": 200, "body": "{\"message\": \"Success\", \"event\": {\"test\": \"data\"}}"}

# View logs
aws logs tail /aws/lambda/bball-app-template-nonlive --follow
```

## Key Differences: Go vs Python

| Aspect | Go | Python |
|--------|----|----|
| **Runtime** | `provided.al2023` (custom) | `python3.12` (managed) |
| **Handler** | `bootstrap` (single binary) | `handler.lambda_handler` (function path) |
| **Package** | Single compiled binary | Directory with .py files + dependencies |
| **Dependencies** | Compiled into binary | Included in deployment package |
| **Testing** | `go test` | `pytest` |
| **Build** | Cross-compile (GOOS, GOARCH) | No compilation needed |

## Terraform Changes Summary

The Lambda resource will be **recreated** (destroyed then created) because:
- Runtime changed: `provided.al2023` → `python3.12`
- Handler changed: `bootstrap` → `handler.lambda_handler`
- Package structure changed: single binary → directory

**This means:**
- New Lambda function ARN (will be different)
- Need to update any services that invoke the Lambda
- CloudWatch log group may be recreated

## Troubleshooting

### If tests fail locally:
```powershell
# Make sure you're in venv
.\venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements-dev.txt

# Run with verbose output
pytest tests/ -v -s
```

### If workflow fails on GitHub:
1. Check Actions tab for error details
2. Common issues:
   - Missing requirements-dev.txt (already created ✅)
   - Import errors (check src/ structure)
   - Terraform state issues (may need force-unlock)

### If Lambda deployment fails:
```powershell
# Check Terraform logs
cd terraform/resources
terraform init -backend-config=backend.hcl
terraform plan -var="environment=nonlive"

# If state is locked:
aws dynamodb delete-item `
  --table-name terraform-state-lock `
  --key '{"LockID": {"S": "tfstate-590183661886-eu-west-3/resources/nonlive/bball-app-template.tfstate-md5"}}'
```

## File Cleanup Checklist

After confirming Python version works:

- [ ] Delete `cmd/` directory
- [ ] Delete `internal/` directory
- [ ] Delete `go.mod`
- [ ] Delete `go.sum`
- [ ] Delete `main.go` (if exists at root)
- [ ] Delete `main_test.go` (if exists at root)
- [ ] Update .gitignore to remove Go-specific entries and add Python ones:
  ```
  # Python
  __pycache__/
  *.py[cod]
  *$py.class
  *.so
  .Python
  venv/
  ENV/
  .pytest_cache/
  .coverage
  htmlcov/
  
  # Remove Go entries
  ```

## Summary

✅ **Completed:**
- Python Lambda handler created
- Tests created and configured
- Terraform updated for Python runtime
- Workflows updated for Python build/test
- Documentation updated

⏳ **You need to do:**
1. Test locally with pytest
2. Deploy via Terraform or push to GitHub
3. Clean up old Go files
4. Update .gitignore

The migration is complete from a code perspective. The infrastructure will be updated when you apply Terraform or push to GitHub.
