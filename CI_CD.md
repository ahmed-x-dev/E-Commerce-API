# CI/CD Pipeline Documentation

This project uses GitHub Actions for continuous integration and delivery.

---

## 📋 Workflows Overview

### 1. **Tests** (`.github/workflows/test.yml`)

**Triggers:** Push to `main`/`develop`, Pull Requests

**What it does:**
- Sets up PostgreSQL & Redis test containers
- Installs dependencies
- Runs linting (flake8)
- Runs pytest with coverage
- Uploads coverage reports to Codecov

**Key Environment Variables:**
- `DATABASE_URL`: Points to test database (PostgreSQL)
- `REDIS_URL`: Points to test Redis
- `DEBUG`: Set to false for CI

**Coverage:** Reports uploaded to [codecov.io](https://codecov.io) (optional)

---

### 2. **Docker Build & Push** (`.github/workflows/docker-build.yml`)

**Triggers:** Push to `main`/`develop`, Tags (`v*`), Pull Requests (build only, no push)

**What it does:**
- Builds Docker image using BuildKit
- Caches layers for faster rebuilds
- Pushes to GitHub Container Registry (GHCR)
- Automatically tags images:
  - Branch name (e.g., `main`, `develop`)
  - Git tags (e.g., `v1.0.0`)
  - Commit SHA (e.g., `main-abc123`)
  - `latest` tag for main branch

**Push behavior:**
- ✅ **Pushes on:** main, develop branches + tags
- ❌ **No push on:** Pull requests (build-only to verify)

**Usage:**
```bash
# Pull the latest image
docker pull ghcr.io/<your-username>/<repo>:latest

# Pull from specific branch
docker pull ghcr.io/<your-username>/<repo>:main
docker pull ghcr.io/<your-username>/<repo>:develop

# Pull from version tag
docker pull ghcr.io/<your-username>/<repo>:v1.0.0
```

---

### 3. **Security & Dependencies** (`.github/workflows/security.yml`)

**Triggers:** Push to `main`/`develop`, Pull Requests, Daily (2 AM UTC)

**What it does:**
- Checks for known vulnerabilities with [Safety](https://safety.io/)
- Checks for outdated packages with [pip-audit](https://github.com/pypa/pip-audit)
- Runs CodeQL static analysis (GitHub's security scanner)

**Reports:** Available in GitHub Security tab (Dependabot alerts, CodeQL results)

---

## 🔧 Setup Instructions

### 1. **Push to GitHub**

If not already on GitHub, initialize:

```bash
git init
git add .
git commit -m "Initial commit: E-Commerce API with CI/CD"
git branch -M main
git remote add origin https://github.com/<username>/<repo>.git
git push -u origin main
```

### 2. **Enable GitHub Actions**

GitHub Actions is enabled by default. Verify:
1. Go to your repo on GitHub
2. Click **Settings** → **Actions** → **General**
3. Ensure "Allow all actions and reusable workflows" is selected

### 3. **Configure GHCR (for Docker pushing)**

Your GitHub Token is automatically available. Docker will push to:
```
ghcr.io/<github-username>/<repo-name>:tag
```

To pull images locally:
```bash
docker login ghcr.io
# Username: <github-username>
# Password: <GitHub Personal Access Token>

docker pull ghcr.io/<github-username>/<repo>:latest
```

### 4. **Set Up Codecov (Optional)**

For coverage reports:
1. Go to [codecov.io](https://codecov.io)
2. Sign in with GitHub
3. Enable the repository
4. No secrets needed (public repos)

---

## 📊 Workflow Status & Monitoring

### View Workflow Runs

1. Go to your GitHub repo
2. Click **Actions** tab
3. See all workflow runs and their status

### Check Specific Workflow

```bash
# List recent workflow runs
gh run list --repo <owner>/<repo>

# View specific run details
gh run view <run-id>

# Watch a run in real-time
gh run watch
```

### Badges (add to README.md)

```markdown
![Tests](https://github.com/<owner>/<repo>/actions/workflows/test.yml/badge.svg)
![Docker Build](https://github.com/<owner>/<repo>/actions/workflows/docker-build.yml/badge.svg)
[![codecov](https://codecov.io/gh/<owner>/<repo>/branch/main/graph/badge.svg)](https://codecov.io/gh/<owner>/<repo>)
```

---

## 🚀 Deployment Strategy

Currently, workflows only:
- ✅ Run tests
- ✅ Build Docker images
- ✅ Push to GHCR

**To add deployment** (future):

1. **To AWS ECS:**
   ```yaml
   - name: Deploy to AWS ECS
     run: |
       aws ecs update-service --cluster prod --service api \
         --force-new-deployment
   ```

2. **To DigitalOcean App Platform:**
   ```yaml
   - name: Deploy to DigitalOcean
     uses: digitalocean/app_action@main
   ```

3. **To Heroku:**
   ```yaml
   - name: Deploy to Heroku
     uses: akhileshns/heroku-deploy@v3.12.12
   ```

---

## 🔐 Secrets Configuration

Current workflows use:
- ✅ `GITHUB_TOKEN` (automatically provided)

For future deployments, add secrets:

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Add secret: `<SECRET_NAME>`
3. Use in workflow: `${{ secrets.SECRET_NAME }}`

**Example secrets to add later:**
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `DATABASE_URL` (prod)
- `STRIPE_API_KEY` (prod)
- `DOCKER_USERNAME` (if using Docker Hub instead of GHCR)
- `DOCKER_PASSWORD`

---

## 🧪 Testing Locally to Match CI

### Run Tests Like CI Does

```powershell
# Start test services
docker-compose -f docker-compose.test.yml up -d

# Install dependencies
pip install -r requirements.txt

# Set environment variables
$env:DATABASE_URL = "postgresql+asyncpg://test_user:test_password@localhost:5434/test_ecommerce_api"
$env:REDIS_URL = "redis://localhost:6380"

# Run tests
pytest -v

# With coverage
pytest --cov=app --cov-report=html

# Cleanup
docker-compose -f docker-compose.test.yml down -v
```

---

## 📈 Performance Tips

### Speed Up Tests

1. **Parallel test execution:**
   ```bash
   pip install pytest-xdist
   pytest -n auto
   ```

2. **Use Docker cache:**
   - GitHub Actions caches automatically (with gha backend)
   - Layers are reused across runs

3. **Skip slow tests in CI:**
   ```python
   @pytest.mark.slow
   def test_something_slow():
       pass
   ```
   
   Then run: `pytest -m "not slow"`

### Docker Build Optimization

- Multistage builds (to reduce image size)
- Separate dev dependencies from prod
- Use smaller base image (already using `python:3.12-slim`)

---

## 🚨 Troubleshooting

### Tests Failing in CI but Passing Locally

1. **Check environment variables** match exactly
2. **Database/Redis ports** differ in CI (5434, 6380 vs 5433, 6379)
3. **Python version mismatch**: CI uses Python 3.12, verify locally
4. **Timezone issues**: CI runs in UTC

**Solution:** Run locally in Docker to match CI environment:
```bash
docker-compose -f docker-compose.test.yml up -d
pytest
```

### Docker Push Failures

**Cause:** Not authenticated to GHCR

**Fix:**
```bash
docker logout ghcr.io
docker login ghcr.io -u <username> -p $(gh auth token)
docker push ghcr.io/<username>/<repo>:latest
```

### Coverage Not Uploading

**Cause:** Codecov token not set (optional for public repos)

**Fix:** Just skip it (already set to `continue-on-error: true`)

---

## 📝 Branching Strategy

Recommended for this CI/CD setup:

```
main          ← Production-ready, all tests passing
  ↑
develop       ← Development, integration branch
  ↑
feature/*     ← Feature branches, PR required
```

**Workflow:**
1. Create feature branch: `git checkout -b feature/new-auth`
2. Push: `git push origin feature/new-auth`
3. Create PR → Triggers tests + build
4. All checks pass? Merge to `develop`
5. Ready to ship? Create release tag → Merges to `main` + deploys

---

## 🎯 Next Steps

1. ✅ Workflows are configured
2. ✅ Push to GitHub
3. ✅ Watch workflows run in Actions tab
4. 📝 Update README with badges
5. 🔐 Add deployment secrets when ready
6. 🚀 Add deployment workflows for production

---

**Need help?** Check GitHub Actions logs for detailed error messages!
