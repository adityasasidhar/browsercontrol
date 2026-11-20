# Project Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add docling-style governance, contribution flow, DCO, and hardened CI/pre-commit to BrowserControl, scaled for a solo maintainer.

**Architecture:** Mostly config and docs files under repo root and `.github/`. Two small Python scripts (max-lines check) live in `scripts/checks/` and are unit-tested. Each task is independently committable on a feature branch.

**Tech Stack:** GitHub Actions, pre-commit, uv, ruff, pytest, Dependabot, Codecov.

**Spec:** `docs/superpowers/specs/2026-11-21-project-foundation-design.md`

## Global Constraints

- Work on a new branch (e.g. `chore/project-foundation`), never directly on `main`; commit only when the user asks.
- Conventional Commits; every commit signed off (`git commit -s`) once DCO is in place.
- `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy browsercontrol/`, `uv run pytest`, `uv run --extra docs mkdocs build --strict` must stay green.
- Repo URL: `https://github.com/adityasasidhar/browsercontrol`; maintainer: Aditya Sasidhar (`@adityasasidhar`). No invented emails: security/conduct contact uses GitHub private vulnerability reporting / issues; leave an explicit `TODO(maintainer)` where an email is needed.
- Actions pinned to full commit SHA with a `# vX.Y.Z` comment; look SHAs up with `gh api repos/<owner>/<repo>/git/ref/tags/<tag> --jq .object.sha` (dereference annotated tags via `git/tags/<sha>`).
- Workflows set top-level `permissions: contents: read` and widen per job only.
- Never commit secrets; Codecov uses the `CODECOV_TOKEN` repo secret.

## Review Focus

- Max-lines script given a deleted/renamed/binary file path: must skip, not crash.
- Max-lines script on a file exactly at the limit: passes; limit+1: fails.
- PR title check with scope and breaking marker (`feat(tools)!: x`): passes; `Update stuff`: fails.
- DCO check on a merge commit or bot (dependabot) commit: must not block.
- Codecov upload on fork PRs (no secret): must not fail CI.

---

### Task 1: Governance and community files

**Files:**
- Create: `MAINTAINERS.md`, `CODE_OF_CONDUCT.md`, `CITATION.cff`, `CHANGELOG.md`, `.github/SECURITY.md`

- [ ] **Step 1:** `MAINTAINERS.md`: one maintainer, Aditya Sasidhar, linked to GitHub; note contact is via issues/GitHub profile.
- [ ] **Step 2:** `CODE_OF_CONDUCT.md`: Contributor Covenant 2.1 (short text, linking to the canonical page, as docling does); enforcement contact `TODO(maintainer)` placeholder, with GitHub private contact as the fallback.
- [ ] **Step 3:** `.github/SECURITY.md`: supported versions (latest 0.x), report via GitHub private vulnerability advisories (`https://github.com/adityasasidhar/browsercontrol/security/advisories/new`), expected response times, scope note (browser automation runs with the user's profile data).
- [ ] **Step 4:** `CITATION.cff`: `cff-version: 1.2.0`, title BrowserControl, author, version `0.2.0`, license MIT, repository URL.
- [ ] **Step 5:** `CHANGELOG.md`: Keep a Changelog format with an `Unreleased` section and a `0.2.0` entry derived from `git log --oneline`.
- [ ] **Step 6:** Verify: `uv run pre-commit run --files MAINTAINERS.md CODE_OF_CONDUCT.md CITATION.cff CHANGELOG.md .github/SECURITY.md`. Expected: all hooks pass. Commit: `docs: add governance and community files`.

### Task 2: Issue and PR templates, CONTRIBUTING updates

**Files:**
- Create: `.github/ISSUE_TEMPLATE/bug_report.md`, `feature_request.md`, `question.md`, `config.yml`, `.github/PULL_REQUEST_TEMPLATE.md`
- Modify: `CONTRIBUTING.md`

- [ ] **Step 1:** Issue templates modeled on docling's: bug template asks for BrowserControl version, OS, Python, MCP client, repro steps, logs (`LOG_LEVEL=DEBUG`); `config.yml` sets `blank_issues_enabled: false` and links to security policy and docs.
- [ ] **Step 2:** PR template: summary, linked issue, type of change, checklist (tests added, docs/`server.py` instructions updated if tool interface changed, `ruff`/`mypy`/`pytest` run, commits signed off).
- [ ] **Step 3:** CONTRIBUTING: add sections on Conventional Commit PR titles (list allowed types matching Task 4 regex), DCO (`git commit -s`, how to amend: `git commit --amend -s --no-edit`, rebase: `git rebase --signoff main`), and links to CODE_OF_CONDUCT / SECURITY.
- [ ] **Step 4:** Verify `uv run pre-commit run --all-files` and `uv run --extra docs mkdocs build --strict`. Commit: `docs: add issue/PR templates and contribution rules`.

### Task 3: Max-lines check (TDD)

**Files:**
- Create: `scripts/checks/check_max_lines.py`, `tests/test_check_max_lines.py`
- Modify: `.pre-commit-config.yaml`, `pyproject.toml` (add `scripts` to ruff/mypy coverage only if needed)

**Interfaces:**
- Produces: `check_max_lines.main(argv: list[str] | None = None) -> int` taking `--max-lines N` (default 800) and file paths; returns 1 if any text file exceeds N lines, else 0; skips missing and non-UTF-8 files.

- [ ] **Step 1:** Write tests in `tests/test_check_max_lines.py` (import the script via `importlib` from its path): file with exactly N lines → returns 0; N+1 → returns 1 and prints the path; nonexistent path → 0; binary bytes file → 0.
- [ ] **Step 2:** `uv run pytest tests/test_check_max_lines.py -v` → FAIL (module missing).
- [ ] **Step 3:** Implement `main` as above in `scripts/checks/check_max_lines.py` with full type hints (mypy strict).
- [ ] **Step 4:** Same pytest command → PASS.
- [ ] **Step 5:** Add a local `max-lines` hook to `.pre-commit-config.yaml` (`entry: python3 scripts/checks/check_max_lines.py`, `args: [--max-lines=800]`, `language: system`, files `\.(py|md|yml|yaml|toml)$`, exclude `uv.lock`, `docs/llms.txt`). Largest current file is 550 lines, so `pre-commit run --all-files` must pass.
- [ ] **Step 6:** Commit: `chore: add max-lines pre-commit check`.

### Task 4: DCO and PR title workflows

**Files:**
- Create: `.github/dco.yml`, `.github/workflows/pr-checks.yml`

- [ ] **Step 1:** `.github/dco.yml` with `allowRemediationCommits: {individual: true}` (same as docling) for the DCO GitHub App.
- [ ] **Step 2:** `pr-checks.yml`, trigger `pull_request` (`opened, edited, synchronize, reopened`), `permissions: contents: read`, concurrency cancel-in-progress. Job `pr-title`: bash step validating `${{ github.event.pull_request.title }}` passed via `env:` (not interpolated into the script) against `^(fix|feat|docs|style|refactor|perf|test|build|ci|chore|revert)(\(.+\))?!?: .+`.
- [ ] **Step 3:** Job `dco`: checkout with `fetch-depth: 0`, loop over `git rev-list --no-merges origin/${{ base }}..HEAD`, fail if a commit lacks a `Signed-off-by:` trailer matching its author; skip authors ending in `[bot]`. Prints how to fix.
- [ ] **Step 4:** Verify locally by running the regex against samples: `feat(tools)!: x` and `fix: y` pass; `Update stuff` fails. Validate YAML with `uv run pre-commit run check-yaml --all-files`. Commit: `ci: add PR title and DCO checks`.

### Task 5: Pin actions and least-privilege permissions

**Files:**
- Modify: `.github/workflows/ci.yml`, `docs.yml`, `release.yml`, `dependency-review.yml`

- [ ] **Step 1:** For each distinct `uses:` (see list: checkout@v4, configure-pages@v5, dependency-review-action@v4, deploy-pages@v4, download-artifact@v4, upload-artifact@v4, upload-pages-artifact@v3, setup-uv@v3/v5, gh-action-pypi-publish@release/v1) resolve the SHA via `gh api` and replace with `owner/repo@<sha> # <tag>`. Unify `setup-uv` to one version.
- [ ] **Step 2:** Add `permissions: contents: read` at top of `ci.yml`, and `concurrency: {group: ${{ github.workflow }}-${{ github.event.pull_request.number || github.ref }}, cancel-in-progress: true}`; keep existing wider permissions in `docs.yml`/`release.yml` job-level.
- [ ] **Step 3:** Verify: `grep -En "uses: .*@v[0-9]" .github/workflows/*.yml` returns nothing; YAML hook passes. Commit: `ci: pin actions to SHAs and tighten permissions`.

### Task 6: Dependabot and Codecov

**Files:**
- Create: `.github/dependabot.yml`, `.github/codecov.yml`
- Modify: `.github/workflows/ci.yml`

- [ ] **Step 1:** `dependabot.yml` version 2: ecosystems `uv` (or `pip` if `uv` unsupported by the validator) at `/` and `github-actions` at `/`, weekly, `open-pull-requests-limit: 5`, commit-message prefix `chore(deps)`/`ci(deps)`.
- [ ] **Step 2:** `codecov.yml`: project status target `auto` with 2% threshold, patch target 70%, `comment` layout `condensed_header, diff, files`.
- [ ] **Step 3:** In `ci.yml` test job on Linux only: run `uv run pytest --cov=browsercontrol --cov-report=xml`, then `codecov/codecov-action` (SHA-pinned) with `token: ${{ secrets.CODECOV_TOKEN }}`, `fail_ci_if_error: false`, `if: ${{ !github.event.pull_request.head.repo.fork }}`-style guard so fork PRs don't fail.
- [ ] **Step 4:** Verify `uv run pytest --cov=browsercontrol --cov-report=xml` passes locally; YAML hook passes. Commit: `ci: add dependabot and codecov`.

### Task 7: Makefile and pre-commit refresh

**Files:**
- Create: `Makefile`
- Modify: `.pre-commit-config.yaml`, `CLAUDE.md` (Commands section, one line pointing to `make help`)

- [ ] **Step 1:** `Makefile` with `.PHONY` targets `help` (default, prints targets), `install`, `browsers`, `lint`, `format`, `typecheck`, `security`, `test`, `cov`, `docs`, `check` (lint+typecheck+test), `pre-commit`; each wraps the exact `uv run ...` command from CLAUDE.md.
- [ ] **Step 2:** Update pre-commit revs: `ruff-pre-commit`, `pre-commit-hooks`, `bandit` to latest tags (look up with `uv run pre-commit autoupdate`, then review the diff); add `uv-pre-commit` `uv-lock` hook; add `fail_fast: true`; keep `check-json`, `mixed-line-ending`.
- [ ] **Step 3:** Run `uv run pre-commit run --all-files`, fix any newly flagged issues (ruff upgrades may add findings; fix minimal), then `make check`. Expected: all pass.
- [ ] **Step 4:** Commit: `chore: add Makefile and refresh pre-commit hooks`.

### Task 8: Final verification

- [ ] **Step 1:** Run `make check`, `uv run bandit -c pyproject.toml -r . --exclude ./tests,./.venv`, `uv run --extra docs mkdocs build --strict`; report outputs.
- [ ] **Step 2:** Report what could not be verified locally (GitHub-side: DCO app install, Codecov secret, Dependabot, branch protection requiring the new checks) and list the manual maintainer steps.
