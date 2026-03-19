---
description: Backend Developer workflow — adding inspectors, code style, plugin pattern
---

# 🔧 Backend Developer Workflow

## Adding a New Hardware Inspector

// turbo-all

### Step 1: Create the inspector file

Create `src/info_machine/inspectors/<name>.py`:

```python
from info_machine.core.inspector import BaseInspector

class MyInspector(BaseInspector):
    name = "my_component"
    display_name = "My Component"

    def collect(self) -> dict:
        """Collect hardware data. Return a dict of findings."""
        return {"model": "...", "status": "..."}

    def health_score(self) -> int:
        """Return 0-100 health score."""
        return 100

    def health_details(self) -> str:
        """Return human-readable health description."""
        return "Component is healthy"
```

### Step 2: Register the inspector

Add import in `src/info_machine/inspectors/__init__.py`:

```python
from .my_component import MyInspector
```

### Step 3: Add tests

Create `tests/test_inspectors/test_my_component.py` with mocked system calls.

### Step 4: Update docs

Add the new inspector to README.md feature list and CHANGELOG.md.

## Code Style

1. Format code
```bash
black src/ tests/
```

2. Lint code
```bash
ruff check src/ --fix
```

3. Type hints are required for all public functions

## Development Setup

1. Create virtual environment
```bash
python -m venv .venv && .venv\Scripts\activate
```

2. Install in dev mode
```bash
pip install -e ".[dev]"
```

3. Run the CLI
```bash
info-machine scan
```
