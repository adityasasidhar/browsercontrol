# Code Formatting and Quality

This project uses automated code formatting and linting tools to maintain code quality.

## Tools

- **[Ruff](https://github.com/astral-sh/ruff)** - Fast Python linter and formatter
- **[Pre-commit](https://pre-commit.com/)** - Git hooks for automated checks
- **[Prettier](https://prettier.io/)** - Markdown/YAML/JSON formatting
- **[Bandit](https://bandit.readthedocs.io/)** - Security vulnerability scanner

## Setup

The tools are already configured. To install the pre-commit hooks:

```bash
uv sync
uv run pre-commit install
```

## Usage

### Manual Formatting

```bash
# Check for linting issues
uv run ruff check .

# Auto-fix linting issues
uv run ruff check . --fix

# Format code
uv run ruff format .

# Run all pre-commit hooks manually
uv run pre-commit run --all-files
```

### Automatic Formatting

Pre-commit hooks run automatically on `git commit`. They will:

1. Run ruff linter and formatter
2. Trim trailing whitespace
3. Fix end-of-file issues
4. Format markdown/YAML/JSON with prettier
5. Check for security issues with bandit

If any hook fails, the commit will be aborted and files will be auto-fixed. Review the changes and commit again.

## Configuration

### Ruff

Configuration in `pyproject.toml`:

- **Line length**: 100 characters
- **Target Python**: 3.11+
- **Enabled rules**: pycodestyle, pyflakes, isort, pep8-naming, pyupgrade, bugbear, comprehensions, simplify, type-checking, Ruff-specific
- **Ignored rules**: E501 (line too long), B008 (function call in defaults), N805 (first arg naming), SIM117 (nested with), B904 (exception chaining)

### Pre-commit

Configuration in `.pre-commit-config.yaml`:

- Ruff linter and formatter
- General file checks (trailing whitespace, EOF, YAML/TOML/JSON validation, large files, merge conflicts)
- Prettier for markdown formatting
- Bandit for security checks (excludes tests, allows subprocess for Playwright)

## Bypassing Hooks

If you need to bypass pre-commit hooks (not recommended):

```bash
git commit --no-verify
```

## CI Integration

Pre-commit.ci is configured to run automatically on pull requests and can auto-fix issues.
