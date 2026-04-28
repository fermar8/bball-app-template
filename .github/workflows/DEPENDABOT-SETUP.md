# Dependabot Workflows - Setup Guide

## Overview

Two workflows have been created to automate Dependabot PR testing and merging:

1. **dependabot-build.yml** - Runs tests on Dependabot PRs
2. **dependabot-automerge.yml** - Auto-merges passing PRs (except major version updates)

## How It Works

### Build Workflow
- **Triggers:** When Dependabot opens a PR to `main`
- **Tests:** Unit tests, integration tests, Lambda handler verification, Terraform validation
- **Result:** Comments on PR with status

### Auto-Merge Workflow
- **Triggers:** After build workflow succeeds
- **Logic:**
  - ✅ **Minor/Patch updates** → Auto-approve and enable auto-merge (squash)
  - ⚠️ **Major updates** → Comment on PR, require manual review
- **Result:** PR auto-merges if all checks pass and not a major version

## Setup Required

### 1. Repository Permissions (IMPORTANT!)

Navigate to: **Settings → Actions → General → Workflow permissions**

Choose ONE of:
- **Option A (Recommended):** "Read and write permissions" 
- **Option B:** "Read repository contents and packages permissions" + Enable "Allow GitHub Actions to create and approve pull requests"

### 2. Branch Protection (Optional but Recommended)

Go to: **Settings → Branches → main → Add rule**

Configure:
- ✅ Require status checks to pass before merging
- ✅ Require branches to be up to date before merging
- Select required checks: `Build, Test, and Plan (Dependabot)`

### 3. Test the Workflows

**Method 1:** Wait for next Dependabot PR (scheduled daily)

**Method 2:** Manually trigger Dependabot
```bash
# Update a dependency version in requirements.txt
# This will trigger Dependabot to detect the change
```

**Method 3:** Use GitHub API to trigger Dependabot alerts
```bash
gh api repos/fermar8/bball-app-template/dependabot/alerts
```

### 4. Verify Everything Works

1. Open the PR created by Dependabot
2. Check Actions tab - verify "Dependabot - Build and Test" workflow runs
3. Verify workflow completes successfully
4. Check "Dependabot - Auto Merge" workflow runs
5. For minor/patch updates: PR should auto-merge
6. For major updates: PR should have a comment explaining manual review needed

## Applying to Other Repositories

### Quick Copy

Copy these two files to each repository:
```
.github/workflows/dependabot-build.yml
.github/workflows/dependabot-automerge.yml
```

### Repository-Specific Adjustments

If repositories have different structures, update in `dependabot-build.yml`:

**Different Terraform path:**
```yaml
working-directory: ./terraform/YOUR_PATH
```

**Different backend key:**
```yaml
key = "resources/nonlive/YOUR_PROJECT_NAME.tfstate"
```

**No Terraform:**
Remove steps 43-76 (Configure AWS through Terraform Plan)

**Different Python version:**
```yaml
python-version: "3.XX"
```

**Different test commands:**
```yaml
run: YOUR_TEST_COMMAND
```

## Repository List

Add your target repositories here:
- [ ] fermar8/bball-app-template (✅ DONE)
- [ ] fermar8/[repository-2]
- [ ] fermar8/[repository-3]
- [ ] ...

## Troubleshooting

**Workflow doesn't run?**
- Check repository permissions (see step 1)
- Verify Dependabot is enabled: `.github/dependabot.yml` exists
- Check if PR is targeting `main` branch

**Auto-merge doesn't work?**
- Verify "Allow GitHub Actions to create and approve pull requests" is enabled
- Check branch protection rules aren't blocking auto-merge
- Ensure build workflow completed successfully first

**Major version detected incorrectly?**
- Check PR title format in workflow logs
- Update regex pattern in `dependabot-automerge.yml` step "Check if major version update"

## Major Version Update Strategy

Current behavior: **Skip auto-merge for major versions**

To change this:

**Auto-merge everything (not recommended):**
Remove the `if` condition from "Enable auto-merge" step

**Different pattern detection:**
Modify the grep pattern in "Check if major version update" step

## Next Steps

1. ✅ Create workflows (DONE)
2. ⬜ Configure repository permissions
3. ⬜ Test with a Dependabot PR
4. ⬜ Apply to other repositories
5. ⬜ Monitor first few auto-merges

## Additional Resources

- [GitHub Actions Permissions](https://docs.github.com/en/actions/security-guides/automatic-token-authentication)
- [Dependabot Configuration](https://docs.github.com/en/code-security/dependabot/dependabot-version-updates/configuration-options-for-the-dependabot.yml-file)
- [Auto-merge PRs](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/incorporating-changes-from-a-pull-request/automatically-merging-a-pull-request)
