# GitHub Actions Configuration Guide

## 📍 Location

GitHub Actions workflows are located in:
```
.github/workflows/
├── backend-ci.yml    - Backend testing and validation
└── frontend-ci.yml   - Frontend building and testing
```

## 🔍 What Actions Were Created

### 1. **Backend CI** (`backend-ci.yml`)

**Triggers:**
- When PR is created/updated with changes in `backend/` directory
- When code is pushed to `main` or `master` branch

**Jobs:**
- ✅ **Test Job:**
  - Sets up Python 3.11
  - Installs dependencies from requirements.txt
  - Checks Python syntax
  - Runs linting (flake8)
  - Validates imports
  - Checks environment template exists

- ✅ **Build Job:**
  - Verifies Railway configuration files exist
  - Checks start.sh is executable
  - Validates deployment readiness

### 2. **Frontend CI** (`frontend-ci.yml`)

**Triggers:**
- When PR is created/updated with changes in `frontend/` directory
- When code is pushed to `main` or `master` branch

**Jobs:**
- ✅ **Test Job:**
  - Sets up Node.js 18
  - Installs dependencies (npm ci)
  - Runs TypeScript type checking (if applicable)
  - Runs ESLint
  - Builds the application
  - Validates build output

- ✅ **Preview Job:**
  - Runs only on Pull Requests
  - Posts a comment on PR when build succeeds

## 🚀 How to Use

### Automatic Execution

These workflows run automatically when you:
1. Create a Pull Request
2. Push commits to a Pull Request
3. Merge to main/master branch

### View Results

1. Go to GitHub repository
2. Click **"Actions"** tab
3. See all workflow runs
4. Click on a run to see detailed logs

### PR Status Checks

When you create a PR, you'll see:
```
✅ Backend CI / test
✅ Backend CI / build
✅ Frontend CI / test
✅ Frontend CI / preview
```

## ⚙️ Customize Workflows

### Add Environment Secrets

For sensitive data (API keys, tokens):

1. Go to GitHub repo → **Settings** → **Secrets and variables** → **Actions**
2. Click **"New repository secret"**
3. Add secrets like:
   - `AZURE_OPENAI_API_KEY`
   - `QDRANT_API_KEY`
   - etc.

### Use Secrets in Workflow

```yaml
- name: Run tests with secrets
  env:
    AZURE_OPENAI_API_KEY: ${{ secrets.AZURE_OPENAI_API_KEY }}
  run: python -m pytest
```

## 🔧 Modify Workflows

### Change Trigger Branches

```yaml
on:
  push:
    branches: [main, develop, staging]  # Add more branches
```

### Add More Jobs

```yaml
jobs:
  deploy:
    name: Deploy to Railway
    runs-on: ubuntu-latest
    needs: [test, build]
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy
        run: |
          curl -X POST ${{ secrets.RAILWAY_WEBHOOK_URL }}
```

### Add Testing

```yaml
- name: Run unit tests
  working-directory: ./backend
  run: |
    pip install pytest
    pytest tests/
```

## 📊 Status Badges

Add these to your README.md:

```markdown
![Backend CI](https://github.com/caibanThinh200/AI_Batch3-Chill-Dev/workflows/Backend%20CI/badge.svg)
![Frontend CI](https://github.com/caibanThinh200/AI_Batch3-Chill-Dev/workflows/Frontend%20CI/badge.svg)
```

## 🛡️ Branch Protection

Enable required status checks:

1. Go to **Settings** → **Branches**
2. Add rule for `main` branch
3. Enable "Require status checks to pass before merging"
4. Select:
   - ✅ Backend CI / test
   - ✅ Backend CI / build
   - ✅ Frontend CI / test

## 🔍 Debugging Failed Actions

### View Logs

1. Go to **Actions** tab
2. Click on failed workflow
3. Click on failed job
4. Expand failed step to see error

### Common Issues

**Issue: Dependencies fail to install**
```yaml
# Solution: Clear cache
- name: Clear cache
  run: |
    npm cache clean --force  # for frontend
    pip cache purge         # for backend
```

**Issue: Timeout**
```yaml
# Solution: Increase timeout
jobs:
  test:
    timeout-minutes: 30  # Default is 360
```

**Issue: Permission denied**
```yaml
# Solution: Add permissions
permissions:
  contents: read
  pull-requests: write
```

## 📦 Advanced Examples

### Deploy on Tag

```yaml
name: Deploy Release

on:
  push:
    tags:
      - 'v*'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Deploy
        run: echo "Deploying version ${{ github.ref_name }}"
```

### Matrix Testing

```yaml
jobs:
  test:
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11]
        os: [ubuntu-latest, macos-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
```

### Conditional Execution

```yaml
- name: Deploy to production
  if: github.ref == 'refs/heads/main' && github.event_name == 'push'
  run: ./deploy.sh
```

## 📝 Next Steps

1. **Commit the workflows:**
   ```bash
   git add .github/workflows/
   git commit -m "Add GitHub Actions CI/CD workflows"
   git push
   ```

2. **Create a test PR** to see actions in action

3. **Check Actions tab** to verify they run successfully

4. **Customize** based on your needs

## 📚 Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workflow Syntax](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions)
- [GitHub Actions Marketplace](https://github.com/marketplace?type=actions)

## 🆘 Getting Help

If actions fail:
1. Check the logs in Actions tab
2. Review the specific error message
3. Google the error with "GitHub Actions"
4. Ask in GitHub Community: https://github.community

---

**Created:** November 8, 2025
**Status:** Ready to use
**Location:** `.github/workflows/`
