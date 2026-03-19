---
description: Project Lead workflow — release planning, PR reviews, branching strategy
---

# 🎯 Project Lead Workflow

## Branching Strategy

```
main        ← production releases only
  └── develop   ← integration branch
        ├── feature/*   ← new features (e.g. feature/gpu-inspector)
        ├── fix/*       ← bug fixes (e.g. fix/battery-health-calc)
        └── docs/*      ← documentation changes
```

## Commit Convention (Conventional Commits)

```
feat: add GPU inspector module
fix: correct battery health percentage calculation
docs: update README with verify command usage
test: add unit tests for CPU inspector
ci: add GitHub Actions lint workflow
refactor: extract WMI helper to utils
chore: bump version to 0.2.0
```

## PR Review Checklist

// turbo-all

1. Check branch naming follows convention
```bash
git branch --show-current
```

2. Verify all tests pass
```bash
pytest tests/ -v
```

3. Check code style
```bash
ruff check src/ && black --check src/ tests/
```

4. Verify changelog is updated for user-facing changes

5. Ensure docs are updated if public API changed

## Release Workflow

1. Merge `develop` → `main`
2. Tag with semantic version: `git tag -a v0.1.0 -m "Release v0.1.0"`
3. Push tag: `git push origin v0.1.0`
4. GitHub Actions auto-creates release & publishes to PyPI

## Milestone Tracking

- **v0.1.0** — Core CLI + CPU/RAM/Disk inspectors + basic health scoring
- **v0.2.0** — All 8 inspectors + spec verification + report export
- **v0.3.0** — Cross-platform support (Linux/macOS)
- **v1.0.0** — Stable release with full test coverage
