# Founding Engineer — BrowserControl

**Location:** Remote (async-friendly; ±5h overlap with US Eastern or European afternoons preferred)
**Compensation:** Open — cash + meaningful early-stage equity. Cash band and equity % finalized in the offer stage based on experience and location.
**Stack:** Python 3.11+, Playwright, FastMCP, Pillow, pytest, ruff, mypy `--strict`
**Reports to:** Founder (you'll be hire #1)
**Start:** Within 4–8 weeks

---

## About BrowserControl

BrowserControl is an [MCP](https://modelcontextprotocol.io) server that gives any AI agent a real browser it can **see**, **click**, and **type** in — using the **Set of Marks (SoM)** pattern. Instead of fragile selectors, the agent calls `click(7)` and a numbered red box tells it what's at that pixel. It's local, private, zero-cost per action, and already on PyPI as a single `pip install browsercontrol`. The repo is MIT, has CI on Linux/Windows/macOS, and ships ~25 tools across navigation, interaction, forms, devtools, tabs, and recording.

The mission of the company is to make this MCP server **great, popular, well-used, and better** — and we need a founding engineer to help turn a strong prototype into a project that the MCP community picks first.

## Why this role exists

The codebase is solid. The architecture is right. What's missing is the second pair of hands that turns a "looks cool on HN" launch into a project with stable releases, real users filing good issues, a docs site people link to, and a roadmap the community can plan around. That's what you'll do.

## What "founding" means here

You are not joining a company with a 20-person engineering org. You are joining **one** engineer (the founder). Your fingerprints will be on:

- Architecture decisions for v0.2+ (multi-engine support, plugin surface, perf).
- The release process, CI, packaging, and PyPI lifecycle.
- The public voice of the project — PRs you review, issues you triage, Discussions you answer.
- The first 5–10 hires' onboarding experience.

You'll work directly with the founder, with very little ceremony and a lot of context.

## First 90 days — what success looks like

**Days 1–30: Land the launch and stabilize**

- Cut a v0.2 release with one marquee feature (Firefox support *or* mobile emulation presets — your pick after a week of codebase immersion).
- Take ownership of issue triage, PR review, and CI flakes.
- Stand up a docs site (mkdocs or docusaurus — your call) that gets linked from the README.
- Close the top-5 "good first contribution" items from the README (Firefox/WebKit, DOM diffing, accessibility audit, mobile presets, cookie import/export).

**Days 31–60: Build the community surface**

- Ship a public roadmap doc with dates and owners.
- Set up a Discussions tab structure (Ideas / Q&A / Show and Tell).
- Add an MCP-Apps showcase page ("agents built on BrowserControl").
- Write 2 deep-dive blog posts or video walkthroughs.

**Days 61–90: Plan v0.3 with the founder**

- Lead the v0.3 design doc (multi-tab workflows, perf budget, plugin surface).
- Run a community feedback round (3 office hours or async).
- Define and hire the **Developer Advocate** role (Phase 2 of the hiring plan).

## What we look for

**Must-have**

- **5+ years** writing production Python, including `asyncio` end-to-end.
- **Hands-on Playwright experience** (or Puppeteer / Selenium with deep browser-internals curiosity). You know why shadow DOM and same-origin iframes matter, and you've debugged a `page.click` that doesn't actually click.
- **Type-happiness**: comfortable with `mypy --strict` and dataclasses / Pydantic models.
- **OSS instinct**: you can review a PR with empathy, write a good commit message, and answer a GitHub issue without making the user feel dumb.
- **Async-first work style**: you can run a 30-min daily standup, leave a written update, ship a PR, and not need a meeting to make progress.

**Strong signal**

- Built or contributed to an MCP server, an agent harness, or a browser-automation library.
- Shipped a Python package to PyPI (yours or someone else's).
- Comfortable in `pyproject.toml`, `uv`, `pre-commit`, GitHub Actions — not just `pip install` and prayers.
- Written technical content (blog post, conference talk, doc site) that you can link to.

**Nice to have**

- TypeScript / Node (helps when debugging the `mcp` client side or contributing upstream to FastMCP).
- Image processing literacy (Pillow, OpenCV) — the SoM renderer lives here.
- Comfort with WebKit / Gecko internals, not just Chromium.
- Experience building a community around a dev tool.

## What we don't need

- 10+ years at FAANG. We need someone who can ship.
- A manager track. This is an IC role; you mentor by reviewing PRs and pairing.
- An LLM PhD. We use vision-language models as a *user* of our server, not as a *subject-matter* of it.

## The work, day to day

- ~60% coding (Python, Playwright, the occasional JS one-liner injected into the page).
- ~20% code review, issue triage, and PR descriptions.
- ~10% writing — docs, blog drafts, design notes, community replies.
- ~10% async sync with founder — daily standup, weekly roadmap check-in, ad-hoc design chats.

## Compensation & terms

- **Cash:** competitive market band, calibrated at offer stage.
- **Equity:** meaningful founding-stage grant; vesting and exercise terms discussed live.
- **Time off:** 25 days PTO + local public holidays; we slow down over the last 2 weeks of December.
- **Hardware:** laptop + test devices budget (a used Pixel or iPhone for mobile-emulation QA is on us).
- **Work auth:** we hire where you are. We don't sponsor visas for this role right now.

## How to apply

Email **founders@browsercontrol.dev** with:

1. A short note (≤200 words) on one of these: (a) why Set of Marks beats selectors, (b) the most interesting browser-automation bug you've debugged, or (c) what you'd cut from BrowserControl's current surface and why.
2. A link to something you've shipped — a GitHub repo, a PyPI package, a blog post, or a talk. **Production code preferred, but a well-written OSS contribution counts.**
3. Your CV / LinkedIn (optional but speeds things up).

We respond to every application within 5 business days. Selected candidates get a paid 30-minute pair-programming session on a real BrowserControl contribution (see [`founding-engineer-screen.md`](founding-engineer-screen.md)), then a paid 90-minute system design conversation. No whiteboard puzzles, no LeetCode.

## FAQ

**Is this full-time?** Yes.
**Can I keep doing OSS work?** Yes — and we'll actively encourage it.
**Will I be on call?** No on-call rotation today; if we add one, you'll be part of deciding its shape.
**What's the interview process like?** Apply → 30-min screen → 90-min design chat → paid half-day trial (optional, your choice) → offer. We aim for under 2 weeks end-to-end.

---

*Posted under [`docs/jobs/`](.) in the BrowserControl repo. Maintained by the founder. If something here is wrong or outdated, open an issue.*
