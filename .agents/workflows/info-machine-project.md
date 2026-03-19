---
description: Info-Machine project — CLI tool for PC/laptop hardware inspection, health scoring, spec verification
---

# 🖥️ Info-Machine Project Skill

## Project Overview

**info-machine** is a Python CLI tool that inspects PC/laptop hardware specifications,
evaluates component health, and verifies configurations against seller claims.

- **Repo**: https://github.com/tang-vu/info-machine
- **Tech**: Python 3.10+, Click, Rich, psutil, WMI, GPUtil, py-cpuinfo
- **Platform**: Windows primary (WMI-dependent)

## Project Structure

```
info-machine/
├── src/info_machine/
│   ├── cli.py                  # CLI entry point (5 commands: scan, health, verify, report, info)
│   ├── core/
│   │   ├── inspector.py        # BaseInspector ABC + InspectorRegistry
│   │   ├── health.py           # Health scoring engine (0-100, A-F grades)
│   │   ├── verifier.py         # Spec verification vs seller claims (JSON)
│   │   └── reporter.py         # Report export (JSON, Markdown, HTML)
│   ├── inspectors/             # 8 hardware inspectors (auto-registered)
│   │   ├── cpu.py, ram.py, disk.py, gpu.py
│   │   ├── display.py, battery.py, network.py, motherboard.py
│   └── utils/
│       ├── formatting.py       # Rich terminal UI (health bars, tables, colors)
│       └── system.py           # WMI helpers, OS detection, byte formatting
├── tests/                      # pytest tests with mocked system calls
├── build.py                    # PyInstaller build → standalone .exe
├── .github/workflows/          # CI (ruff+black+pytest) + Release (EXE+PyPI)
└── .agents/workflows/          # Dev team workflows
```

## Build & Release Process

### Building Standalone EXE (No Python Required)
```bash
pip install pyinstaller
python build.py
# Output: dist/info-machine.exe
```

### Creating a Release
```bash
# 1. Update version in pyproject.toml and __init__.py
# 2. Update CHANGELOG.md
# 3. Commit changes
git add -A; git commit -m "chore: bump version to v0.x.0"

# 4. Tag and push
git tag -a v0.x.0 -m "Release v0.x.0"
git push origin main; git push origin v0.x.0

# 5. GitHub Actions builds EXE + creates Release automatically

# OR create release manually with gh CLI:
python build.py
gh release create v0.x.0 dist/info-machine.exe --title "v0.x.0" --generate-notes
```

### Updating GitHub Repo Metadata
```bash
gh repo edit --description "Description here"
gh repo edit --add-topic hardware --add-topic cli
```

## Adding a New Inspector

1. Create `src/info_machine/inspectors/<name>.py` extending `BaseInspector`
2. Implement `collect()`, `health_score()`, `health_details()`
3. Add `@registry.register` decorator
4. Import in `src/info_machine/inspectors/__init__.py`
5. Add verifier in `core/verifier.py` if needed
6. Add tests in `tests/test_inspectors/`
7. Update README, CHANGELOG

## Code Standards

- **Formatter**: Black (line-length 100)
- **Linter**: Ruff (E, F, W, I, N, UP, B, SIM)
- **Type hints**: Required on all public functions
- **Docstrings**: Google-style
- **Commits**: Conventional (feat/fix/docs/test/ci/chore)
- **Exceptions**: Always chain with `raise ... from e` (B904)

## Key Patterns

- Inspectors use `@registry.register` decorator for auto-discovery
- `safe_collect()` wraps `collect()` with error handling
- WMI queries go through `utils/system.py:wmi_query()` helper
- Health scores: 0-100, penalize for temp/usage/degradation
- Verifier uses smart matching: model identifier extraction, capacity tolerance (±10%)
