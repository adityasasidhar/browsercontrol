# Contributing to BrowserControl

We love your input! We want to make contributing to BrowserControl as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## 🚀 Quick Start for Contributors

1. **Fork the repo** and clone it locally
2. **Install `uv`** (our package manager):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
3. **Install dependencies**:
   ```bash
   uv sync
   ```
4. **Install Playwright browsers**:
   ```bash
   uv run playwright install chromium
   ```
5. **Run the server in dev mode**:
   ```bash
   uv run fastmcp dev browsercontrol/server.py
   ```

## 🛠️ Development Workflow

We use [uv](https://github.com/astral-sh/uv) for dependency management and packaging. It's fast and reliable.

### Project Structure
- `browsercontrol/server.py`: Main MCP server definition
- `browsercontrol/browser.py`: Core logic (Playwright + Set of Marks)
- `browsercontrol/tools/`: Tool implementations split by category

### Making Changes
1. Create a branch for your feature: `git checkout -b feature/amazing-feature`
2. Implement your changes
3. Run tests (see below)
4. Commit your changes. We like [Conventional Commits](https://www.conventionalcommits.org/).
   - `feat: add new scrolling tool`
   - `fix: handle localhost connection refused`
   - `docs: update troubleshooting guide`

## 🧪 Testing

We use `pytest`. Please ensure all tests pass before submitting a PR.

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_navigation.py
```

If you add a new tool or feature, please add a corresponding test case covering:
- Happy path (it works)
- Error handling (it fails gracefully)

## 📝 Pull Request Process

1. Update the README.md with details of changes to the interface, this includes new environment variables, exposed ports, useful file locations and container parameters.
2. Increase the version numbers in any examples files and the README.md to the new version that this Pull Request would represent.
3. You may merge the Pull Request in once you have the sign-off of two other developers, or if you do not have permission to do that, you may request the second reviewer to merge it for you.

## 🐛 Reporting Bugs

Bugs are tracked as GitHub issues. When filing an issue, please explain the problem and include additional details to help maintainers reproduce the problem:

- Use a clear and descriptive title
- Describe the exact steps which reproduce the problem
- Provide specific examples to demonstrate the steps
- Describe the behavior you observed after following the steps
- Explain which behavior you expected to see instead and why
- Include screenshots/logs if possible

## 📄 License

By contributing, you agree that your contributions will be licensed under its MIT License.
