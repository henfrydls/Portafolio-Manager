# Status Badges

Add these badges to your README.md to show the status of your CI/CD pipelines:

## CI/CD Status

```markdown
![CI Pipeline](https://github.com/henfrydls/henfrydls/workflows/CI%20Pipeline/badge.svg)
![Security Scanning](https://github.com/henfrydls/henfrydls/workflows/Security%20Scanning/badge.svg)
![Deploy](https://github.com/henfrydls/henfrydls/workflows/Deploy/badge.svg)
```

## Code Quality

```markdown
[![codecov](https://codecov.io/gh/henfrydls/henfrydls/branch/main/graph/badge.svg)](https://codecov.io/gh/henfrydls/henfrydls)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
```

## Security

```markdown
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=henfrydls_henfrydls&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=henfrydls_henfrydls)
[![Known Vulnerabilities](https://snyk.io/test/github/henfrydls/henfrydls/badge.svg)](https://snyk.io/test/github/henfrydls/henfrydls)
```

## Build & Deploy

```markdown
[![Docker Image](https://img.shields.io/docker/v/henfrydls/portfolio?label=docker&logo=docker)](https://github.com/henfrydls/henfrydls/pkgs/container/henfrydls)
[![Docker Image Size](https://img.shields.io/docker/image-size/henfrydls/portfolio?logo=docker)](https://github.com/henfrydls/henfrydls/pkgs/container/henfrydls)
```

## Version & Stats

```markdown
[![GitHub release](https://img.shields.io/github/v/release/henfrydls/henfrydls)](https://github.com/henfrydls/henfrydls/releases)
[![GitHub commits since latest release](https://img.shields.io/github/commits-since/henfrydls/henfrydls/latest)](https://github.com/henfrydls/henfrydls/commits/main)
[![GitHub last commit](https://img.shields.io/github/last-commit/henfrydls/henfrydls)](https://github.com/henfrydls/henfrydls/commits/main)
```

## Community

```markdown
[![GitHub issues](https://img.shields.io/github/issues/henfrydls/henfrydls)](https://github.com/henfrydls/henfrydls/issues)
[![GitHub pull requests](https://img.shields.io/github/issues-pr/henfrydls/henfrydls)](https://github.com/henfrydls/henfrydls/pulls)
[![GitHub stars](https://img.shields.io/github/stars/henfrydls/henfrydls?style=social)](https://github.com/henfrydls/henfrydls/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/henfrydls/henfrydls?style=social)](https://github.com/henfrydls/henfrydls/network/members)
```

## Python & Django

```markdown
[![Python Version](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![Django Version](https://img.shields.io/badge/django-4.2-green.svg)](https://www.djangoproject.com/)
[![PostgreSQL](https://img.shields.io/badge/postgresql-15-blue.svg)](https://www.postgresql.org/)
```

## Complete Example for README.md

```markdown
# Henfry De Los Santos - Portfolio

![CI Pipeline](https://github.com/henfrydls/henfrydls/workflows/CI%20Pipeline/badge.svg)
![Security Scanning](https://github.com/henfrydls/henfrydls/workflows/Security%20Scanning/badge.svg)
[![codecov](https://codecov.io/gh/henfrydls/henfrydls/branch/main/graph/badge.svg)](https://codecov.io/gh/henfrydls/henfrydls)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![Django Version](https://img.shields.io/badge/django-4.2-green.svg)](https://www.djangoproject.com/)

Professional Django portfolio website with multilingual support, modern UI, and comprehensive testing.

[Your existing content here...]
```

## Setting Up External Services (Optional)

### Codecov
1. Sign up at https://codecov.io
2. Connect your GitHub repository
3. Add `CODECOV_TOKEN` to GitHub Secrets

### SonarCloud
1. Sign up at https://sonarcloud.io
2. Import your repository
3. Add `SONAR_TOKEN` to GitHub Secrets

### Snyk
1. Sign up at https://snyk.io
2. Connect your GitHub repository
3. Add `SNYK_TOKEN` to GitHub Secrets
