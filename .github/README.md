# GitHub Actions CI/CD Documentation

This directory contains the complete CI/CD pipeline configuration for the Henfry De Los Santos Portfolio project.

## 🚀 Workflows Overview

### 1. **CI Pipeline** (`ci.yml`)
**Triggers:** Push to main/develop/refactor branches, Pull Requests

**Jobs:**
- ✅ **Linting & Code Quality**
  - Black (code formatting)
  - isort (import sorting)
  - Flake8 (PEP 8 compliance)
  - Pylint (deep code analysis)

- 🔒 **Security Analysis**
  - Bandit (security linter)
  - Safety (dependency vulnerability checking)

- 🧪 **Testing & Coverage**
  - 96 unit tests
  - Coverage reporting (51% global, 70%+ critical areas)
  - PostgreSQL 15 integration
  - Redis integration

- 🐳 **Docker Build Validation**
  - Multi-platform build test
  - Docker Compose validation

**Status:** Required for all PRs

---

### 2. **Security Scanning** (`security.yml`)
**Triggers:** Push, PRs, Scheduled (Weekly Mondays 9 AM UTC)

**Jobs:**
- 🔍 **CodeQL Analysis** (Python & JavaScript)
- 📦 **Dependency Review**
- 🛡️ **SAST with Semgrep**
- 🔐 **Secret Detection** (Gitleaks)
- 🐳 **Docker Image Scanning** (Trivy)
- ⚠️ **OWASP Dependency Check**

**Output:** SARIF reports uploaded to GitHub Security tab

---

### 3. **PR Checks** (`pr-checks.yml`) - Simplified
**Triggers:** Pull Request events

**Jobs:**
- ✍️ **PR Validation**
  - Semantic PR title checking (feat, fix, docs, etc.)
  - PR size labeling (XS to XL)

- 📊 **Complexity Analysis**
  - Cyclomatic complexity check with Radon
  - Maintainability index
  - Warnings for high complexity functions

**Note:** AI Code Review, Coverage Diff, and Performance checks removed to simplify workflow

---

### 4. **Release** (`release.yml`) - Manual Use
**Triggers:** Version tags (v*.*.*), Manual dispatch

**Jobs:**
- 📝 **Create Release**
  - Automated changelog generation
  - Release notes creation
  - Metrics inclusion

- 🏗️ **Build Release Artifacts**
  - Multi-platform Docker images (AMD64, ARM64)
  - Tagged with version

- 📋 **Generate SBOM**
  - Software Bill of Materials
  - Attached to release

- 📦 **Publish to PyPI** (Optional, disabled by default)
- 📢 **Notifications**

**How to Use:**
1. Create a version tag: `git tag -a v1.0.0 -m "Release 1.0.0"`
2. Push tag: `git push origin v1.0.0`
3. Workflow runs automatically
4. See `docs/RELEASE_WORKFLOW.md` for complete guide

---

### 5. **Validate** (`validate.yml`)
**Triggers:** Workflow changes, Pull Requests

**Jobs:**
- ✅ **Workflow Syntax Validation**
- ✅ **Configuration File Validation**
- 🐳 **Docker Build Test**

---

## 🔧 Configuration Files

### Code Quality
- **`.flake8`** - Flake8 linting configuration
- **`pyproject.toml`** - Black, isort, pytest, coverage settings
- **`.github/dependabot.yml`** - Automated dependency updates

### Required Secrets

Add these to your GitHub repository secrets:

#### Required
- `GITHUB_TOKEN` - Automatically provided by GitHub Actions

#### Optional (for enhanced features)
- `CODECOV_TOKEN` - For coverage reporting to Codecov
- `OPENAI_API_KEY` - For AI code reviews
- `SLACK_WEBHOOK` - For deployment notifications
- `SEMGREP_APP_TOKEN` - For Semgrep scanning
- `GITLEAKS_LICENSE` - For Gitleaks secret scanning
- `PYPI_API_TOKEN` - For PyPI publishing
- `SONAR_TOKEN` - For SonarCloud integration
- `SNYK_TOKEN` - For Snyk security scanning

---

## 📊 Coverage & Quality Gates

### Current Metrics
- **Global Coverage:** 51%
- **Critical Areas Coverage:** 70-80%
- **Tests:** 96 passing, 0 failing
- **Security:** All checks passing ✅

### Quality Gates
- ✅ Tests must pass (required)
- ⚠️ Coverage should not decrease
- ⚠️ No high/critical security vulnerabilities
- ⚠️ Code complexity below threshold
- ℹ️ Linting warnings allowed (non-blocking)

---

## 🎯 Branch Strategy

```
main (protected)
├── develop
├── feature/*
├── bugfix/*
├── refactor/*
└── hotfix/*
```

### Branch Protection Rules

**`main` branch:**
- Requires PR approval
- Requires status checks to pass:
  - CI Pipeline
  - Security Scanning
  - Code Review
- No force pushes
- No deletions

**`develop` branch:**
- Requires status checks to pass
- No force pushes

---

## 🚀 Quick Start

### Running Workflows Locally

#### 1. Install act (GitHub Actions local runner)
```bash
# macOS
brew install act

# Linux
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Windows
choco install act-cli
```

#### 2. Run CI pipeline locally
```bash
act -j test
```

#### 3. Run security scans locally
```bash
act -j security
```

### Running Tests Manually
```bash
# In Docker
docker compose exec web python manage.py test portfolio.tests

# With coverage
docker compose exec web coverage run --source='portfolio' manage.py test portfolio.tests
docker compose exec web coverage report
```

---

## 📈 Monitoring & Observability

### GitHub Insights
- **Actions** → View workflow runs
- **Security** → View vulnerability alerts
- **Insights** → View metrics and trends

### Third-party Integrations
- **Codecov:** Coverage trends and reports
- **SonarCloud:** Code quality metrics
- **Snyk:** Dependency vulnerability monitoring

---

## 🔄 Continuous Improvement

### Automated Updates
Dependabot runs weekly and creates PRs for:
- Python dependencies (Mondays)
- Docker images (Tuesdays)
- GitHub Actions (Wednesdays)

### Scheduled Scans
- Security scans run weekly (Mondays 9 AM UTC)
- Dependency audits included in security scans

---

## 📚 Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Django Testing Guide](https://docs.djangoproject.com/en/4.2/topics/testing/)
- [OWASP Security Guidelines](https://owasp.org/)

---

## 🤝 Contributing

When contributing:
1. Create a feature branch from `develop`
2. Write tests for new features
3. Ensure all CI checks pass
4. Request review from maintainers
5. Merge only after approval

---

## 📞 Support

For issues with CI/CD pipelines:
- Open an issue with the `ci/cd` label
- Check workflow logs in the Actions tab
- Review this documentation

---

**Last Updated:** 2026-01-05
**Maintained By:** Henfry De Los Santos
