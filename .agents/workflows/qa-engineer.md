---
description: QA Engineer workflow — testing strategy, coverage targets, bug reports
---

# 🧪 QA Engineer Workflow

## Testing Strategy

// turbo-all

### Unit Tests
Test each inspector and core module in isolation using mocked system data.

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=info_machine --cov-report=term-missing

# Run specific test file
pytest tests/test_inspectors/test_cpu.py -v
```

### Integration Tests
Test CLI commands end-to-end using Click's test runner.

```bash
pytest tests/test_cli.py -v
```

### Coverage Targets
- **Minimum**: 70% overall
- **Goal**: 85%+ on core modules
- **Inspectors**: Mock-based, 80%+ each

## Test Patterns

### Mocking System Calls
```python
from unittest.mock import patch, MagicMock

@patch("info_machine.inspectors.cpu.psutil")
def test_cpu_collect(mock_psutil):
    mock_psutil.cpu_count.return_value = 8
    mock_psutil.cpu_freq.return_value = MagicMock(current=3200.0)
    inspector = CpuInspector()
    data = inspector.collect()
    assert data["cores"] == 8
```

### CLI Testing
```python
from click.testing import CliRunner
from info_machine.cli import main

def test_scan_command():
    runner = CliRunner()
    result = runner.invoke(main, ["scan"])
    assert result.exit_code == 0
```

## Bug Report Template

```markdown
## Bug Report
**Command**: `info-machine health`
**Expected**: Battery health shows percentage
**Actual**: Shows "N/A" on desktop PC
**Environment**: Windows 11, Python 3.12, no battery present
**Steps to Reproduce**: 1. Run on desktop PC 2. Check battery section
**Severity**: Low (cosmetic)
```

## Pre-Release QA Checklist
- [ ] All tests pass
- [ ] Coverage meets minimum threshold
- [ ] CLI help text is correct for all commands
- [ ] Error handling works for missing hardware (e.g., no GPU, no battery)
- [ ] Output formatting is clean and aligned
- [ ] JSON/HTML/Markdown exports are valid
