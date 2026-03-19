# Contributing to Info-Machine

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/info-machine.git`
3. Create a branch: `git checkout -b feature/my-feature`
4. Install dev dependencies: `pip install -e ".[dev]"`

## Development Workflow

1. Write code following the project's code style
2. Add tests for new functionality
3. Run tests: `pytest tests/ -v`
4. Run linter: `ruff check src/`
5. Format code: `black src/ tests/`
6. Commit with conventional commits: `feat: add XYZ inspector`
7. Push and create a Pull Request

## Commit Convention

Use [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` — New feature
- `fix:` — Bug fix
- `docs:` — Documentation changes
- `test:` — Adding/modifying tests
- `refactor:` — Code refactoring
- `ci:` — CI/CD changes
- `chore:` — Maintenance

## Code Style

- Python 3.10+ with type hints
- Formatted with Black (line length 100)
- Linted with Ruff
- Google-style docstrings

## Adding a New Inspector

See `.agents/workflows/backend-dev.md` for detailed steps.
