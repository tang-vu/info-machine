---
description: DevOps workflow — CI/CD setup, GitHub Actions, PyPI publishing, releases
---

# 🚀 DevOps Workflow

## CI/CD Pipeline

// turbo-all

### GitHub Actions — CI (`.github/workflows/ci.yml`)

Triggered on:
- Push to `develop` and `main`
- Pull requests to `develop` and `main`

Steps:
1. Checkout code
2. Setup Python 3.10, 3.11, 3.12
3. Install dependencies
4. Run `ruff check src/`
5. Run `black --check src/ tests/`
6. Run `pytest tests/ -v --cov=info_machine`

### GitHub Actions — Release (`.github/workflows/release.yml`)

Triggered on: Tag push matching `v*`

Steps:
1. Build package (`python -m build`)
2. Create GitHub Release with changelog
3. Publish to PyPI (`twine upload`)

## Local Dev Environment Setup

1. Clone and setup
```bash
git clone https://github.com/tang-vu/info-machine.git
cd info-machine
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
```

2. Run CI checks locally
```bash
ruff check src/
black --check src/ tests/
pytest tests/ -v --cov=info_machine
```

## Release Process

1. Ensure `develop` is green (all CI checks pass)
2. Update version in `pyproject.toml`
3. Update `CHANGELOG.md`
4. Create PR: `develop` → `main`
5. After merge, tag the release:
```bash
git checkout main
git pull origin main
git tag -a v0.1.0 -m "Release v0.1.0"
git push origin v0.1.0
```
6. GitHub Actions handles the rest

## Package Distribution

```bash
# Build locally
python -m build

# Test install
pip install dist/info_machine-0.1.0-py3-none-any.whl

# Verify CLI works
info-machine --version
```
