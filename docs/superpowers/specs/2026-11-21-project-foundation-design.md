# Project foundation (docling-style) — design

Status: approved by the maintainer in conversation (2026-11-21). **Partly
implemented** (PR #14); checked against the repo on 2026-11-21.

- **Done:** `CHANGELOG.md`, issue and PR templates, CONTRIBUTING (conventional
  commits, DCO), `.github/dco.yml` and the PR-title check (`pr-checks.yml`),
  `Makefile`, the max-lines check, refreshed pre-commit hooks with `uv-lock`,
  least-privilege `permissions` and concurrency in `docs.yml`, `release.yml`,
  and `pr-checks.yml`.
- **Not done:** `MAINTAINERS.md`, `CODE_OF_CONDUCT.md`, `.github/SECURITY.md`,
  `CITATION.cff` (these need maintainer contact details), Dependabot, Codecov,
  actions pinned to commit SHAs, and `permissions`/`concurrency` in `ci.yml`.
- **Changed since approval:** Tach *was* adopted for import boundaries
  (`tach.toml`, pre-commit hook), overriding the non-goal below. The docs moved
  from MkDocs to VitePress, so the `mkdocs build --strict` constraint is now
  `npm run build` plus `npm run check:links` in `docs/`.

## Intent
Give BrowserControl the governance, contribution flow and CI hardening that
docling has, scaled to a solo-maintainer project, so outside contributors and
users can trust and contribute to it.

## Goals
- Governance/community files: `MAINTAINERS.md`, `CODE_OF_CONDUCT.md`,
  `.github/SECURITY.md`, `CITATION.cff`, `CHANGELOG.md`.
- Contribution flow: issue templates (bug, feature, question), PR template,
  CONTRIBUTING updates (conventional commits, DCO sign-off).
- DCO: `.github/dco.yml` plus a sign-off check; contributors use `git commit -s`.
- Conventional-commit PR title check as a GitHub Action (not Mergify).
- Dependabot (pip/uv, github-actions).
- Codecov upload and `.github/codecov.yml`.
- CI hardening: actions pinned to commit SHAs, least-privilege `permissions`,
  concurrency cancellation.
- `Makefile` wrapping the documented commands.
- Max-lines-per-file pre-commit check.
- Refresh pre-commit hook versions; add the `uv-lock` hook.

## Non-goals / anti-goals
- No `tach`, AI-triage workflows, or multi-reviewer approval rules (need a team).
- No IBM-specific contacts or text copied from docling.
- No change to runtime behaviour of the MCP server.

## Approaches
1. Copy docling wholesale — rejected: team-scale machinery a solo project can't use.
2. Scaled-down port (chosen): same structure, lighter enforcement.
3. Only docs files — rejected: misses the automated checks the maintainer asked for.

## Constraints
- Follow CLAUDE.md: Conventional Commits, ruff/mypy/bandit must stay green,
  `mkdocs build --strict` must pass, no secrets committed.
- Maintainer contact details and Codecov token are the maintainer's to supply;
  use placeholders/secrets, never invent them.

## Left to the builder
File wording, exact action SHAs (look up current ones), max-lines threshold
(pick from the current largest file), Makefile target names.
