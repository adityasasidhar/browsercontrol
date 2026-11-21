# Contributing to BrowserControl

Bug reports, fixes, docs, and new tools are all welcome. This file covers the rules a
contribution has to follow. Setup, every check, how to add a tool, how to work on the docs
site, and how releases are cut are in the
[contributing guide](https://adityasasidhar.github.io/browsercontrol/project/contributing)
(source: [`docs/project/contributing.md`](docs/project/contributing.md)).

## Quick start

```bash
git clone https://github.com/<you>/browsercontrol && cd browsercontrol
uv sync                              # runtime and dev dependencies
uv run playwright install chromium   # the browser engine
uv run pre-commit install            # lint and format on commit
make check                           # lint, type-check, and tests
```

You need [uv](https://docs.astral.sh/uv/getting-started/installation/). `make help` lists
every shortcut.

## Making a change

1. Branch from `main`, named after the change type: `feat/…`, `fix/…`, `docs/…`, `chore/…`.
2. Make the change, with tests for the happy path and the error path. If you add or change a
   tool, update its page in `docs/reference/` and regenerate the catalog with
   `uv run python scripts/gen_tools_json.py`; tests fail otherwise.
3. Add a line under `[Unreleased]` in [CHANGELOG.md](CHANGELOG.md) for anything users will
   notice.
4. Run `make check` and `uv run pre-commit run --all-files`.

## Commits and pull requests

- **Conventional Commits** for every commit and for the PR title:
  `type(scope)!: description`, where `type` is one of `feat`, `fix`, `docs`, `style`,
  `refactor`, `perf`, `test`, `build`, `ci`, `chore`, or `revert`. CI checks the PR title.
- **Sign off every commit** with `git commit -s`. This certifies the
  [Developer Certificate of Origin](https://developercertificate.org/), and CI rejects
  commits without a `Signed-off-by` line. To sign off commits you already made:
  `git rebase --signoff origin/main && git push --force-with-lease`.
- **In the PR description**, explain the user-visible change, link related issues, and
  attach screenshots for visual or docs-site changes. The PR template lists the rest.
- The maintainer reviews and merges. CI must be green first.

## Reporting bugs

Open a [GitHub issue](https://github.com/adityasasidhar/browsercontrol/issues/new/choose)
using the bug report template. Include the exact steps to reproduce, what you expected,
what happened instead, your OS, client, and BrowserControl version, and any logs
(`LOG_LEVEL=DEBUG`) or screenshots.

## License

By contributing, you agree that your contributions are licensed under the project's
[MIT License](LICENSE).
