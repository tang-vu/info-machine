---
description: Tech Writer workflow — documentation standards, README, changelogs, inline docs
---

# 📝 Tech Writer Workflow

## Documentation Standards

// turbo-all

### README.md
Must include:
- Project badge (CI status, version, license)
- One-line description
- Feature list
- Installation instructions
- Quick start / usage examples
- Screenshots or terminal output examples
- Contributing link
- License

### Inline Documentation
- All public classes and functions must have docstrings
- Use Google-style docstrings:

```python
def health_score(self) -> int:
    """Calculate component health score.

    Returns:
        int: Score from 0 (critical) to 100 (perfect).

    Raises:
        InspectorError: If data collection fails.
    """
```

### CHANGELOG.md
Follow [Keep a Changelog](https://keepachangelog.com/):

```markdown
## [0.1.0] - 2026-03-19
### Added
- Initial CLI with `scan`, `health`, `verify`, `report`, `info` commands
- CPU, RAM, Disk, GPU, Display, Battery, Network, Motherboard inspectors
- Health scoring system with A-F grades
- Spec verification against seller claims
- JSON, Markdown, HTML report export
```

## When to Update Docs

| Change Type | Update Required |
|---|---|
| New inspector added | README features, CHANGELOG, ARCHITECTURE |
| CLI command added/changed | README usage, `--help` text |
| Bug fix | CHANGELOG |
| API change | Inline docstrings, ARCHITECTURE |
| New dependency | README installation, pyproject.toml |

## Review Checklist

1. Run CLI help and verify it matches README examples
```bash
info-machine --help
info-machine scan --help
```

2. Check all code has docstrings
```bash
python -m pydocstyle src/info_machine/ --convention=google
```

3. Verify CHANGELOG is up to date with latest changes
