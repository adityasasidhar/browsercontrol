# Founding Engineer — Screening Rubric

This rubric is calibrated to the **Priorities** for the Founding Engineer role in the BRO-1 hiring plan. It is used at three gates:

1. **Resume / GitHub screen** (15 min) — fill in column *R* only.
2. **30-minute pair-programming screen** (see [`founding-engineer-screen.md`](founding-engineer-screen.md)) — fill in columns *R* and *S*.
3. **90-minute system-design conversation** — fill in columns *R*, *S*, *D*.

Scoring: **0–2** = reject. **3** = neutral. **4–5** = signal.

Total weight = 100%. A candidate scoring **< 60%** does not proceed. **60–75%** = proceed with reservations. **> 75%** = strong hire.

---

## Criteria

### 1. Python depth & `asyncio` fluency — **25%**

*Maps to BRO-1 FE priority: "ship v0.2 without breaking the public API."*

| Signal | Strong (5) | Acceptable (3) | Weak (1) |
|---|---|---|---|
| Type-hints discipline | Writes `mypy --strict`-clean code unprompted; uses `Protocol`, `TypeVar`, `Literal` | Annotates everything but occasionally reaches for `Any` | Annotates inconsistently; comments instead of types |
| Async intuition | Knows when to use `gather` vs `create_task` vs sequential `await`; understands cancellation, timeouts, and event-loop pitfalls | Writes correct linear async code; slower on concurrency decisions | Mixes sync and async without thinking; has shipped `RuntimeError: Event loop is closed` |
| Packaging & tooling | Comfortable in `pyproject.toml`, `uv`, lockfiles, version pins, build backends | Uses `pip` and `venv` competently | Avoids packaging; has never cut a release |

**R (resume):** Look for OSS contributions in typed-Python repos, `pyproject.toml` files they've authored, packages on PyPI.
**S (screen):** Does their code type-check without help? Do they reach for `asyncio.gather` naturally?
**D (design):** Can they describe how they'd add a graceful-shutdown signal handler to the FastMCP lifespan?

### 2. Playwright / browser-automation intuition — **25%**

*Maps to BRO-1 FE priority: "own the SoM renderer and Shadow DOM / iframe correctness."*

| Signal | Strong (5) | Acceptable (3) | Weak (1) |
|---|---|---|---|
| DOM literacy | Explains the difference between element coordinates and `elementFromPoint` without prompting; knows `contentDocument` and `shadowRoot` quirks | Has shipped Playwright work; needs a hint on shadow DOM | Has used Playwright via tutorials; treats selectors as magic |
| Debugging depth | Talks about a real bug they hit (race conditions, animations, persistent context state, network interception) and what they did | Recalls typical pitfalls at a high level | Has not debugged Playwright beyond what the docs cover |
| SoM-style thinking | Volunteers the idea that *visual coordinates* may disagree with the DOM, and how to reconcile | Understands once prompted | Hasn't thought about it |

**R:** Look for Playwright-related OSS, blog posts, or talk videos.
**S:** Live-debug a screenshot where the SoM element map has shifted after a click. Watch their instinct.
**D:** Ask them to design a test that catches "element coordinates shifted because a banner appeared mid-click."

### 3. MCP / agent-tooling literacy — **15%**

*Maps to BRO-1 FE priority: "be a credible voice in the MCP community."*

| Signal | Strong (5) | Acceptable (3) | Weak (1) |
|---|---|---|---|
| Conceptual grasp | Explains the MCP `tools/list` ↔ `tools/call` loop, JSON-RPC framing, and why tool *schemas* matter for agents | Has read the MCP spec; can talk about it accurately | Vague; confuses MCP with LangChain / LlamaIndex |
| Hands-on | Has built or contributed to an MCP server, even a toy one | Has wired up MCP clients in Cursor / Claude Desktop | Has only read about MCP; no hands-on |
| Forward-looking | Has opinions about MCP-Auth, MCP-Apps, streaming, sampling | Open to the ideas; hasn't thought hard about them | No opinions; treat MCP as a fixed thing |

**R:** GitHub repos with `mcp` in the name, blog posts, talks.
**S:** Ask them to describe the JSON schema for a `click(element_id: int)` tool. Watch for accuracy and any "but what if..." instincts.
**D:** Ask them to design a new MCP tool for BrowserControl that the current README doesn't have. Their choice — quality of reasoning matters more than the choice.

### 4. OSS maintainer instinct & writing — **15%**

*Maps to BRO-1 FE priority: "turn a prototype into a project with stable releases, real users filing good issues, and a roadmap the community can plan around."*

| Signal | Strong (5) | Acceptable (3) | Weak (1) |
|---|---|---|---|
| PR craft | Their PRs have clear titles, small diffs, a test, and a paragraph of context | PRs work; the description is terse | PRs are "fix stuff" with a 2k-line diff |
| Issue communication | Has answered user issues with empathy and reproducibility steps | Reasonable; a bit terse | Doesn't engage; or engages bluntly |
| Writing | Can write a clear technical doc, README section, or design note | Writes competently; occasionally unclear | Writing is hard to follow |

**R:** Read 3 of their GitHub issues or PRs. Read 1 piece of long-form writing (blog post, design doc, conference talk).
**S:** Have them write a 3-sentence PR description live, for the change they just made in the screen. Grade it.
**D:** Give them a real open BrowserControl issue and ask them to draft a public reply as if they were the maintainer.

### 5. Pragmatic velocity & taste — **20%**

*Maps to BRO-1 FE priorities: "ship the top-5 'good first contributions' in 90 days" and "be the second pair of hands."*

| Signal | Strong (5) | Acceptable (3) | Weak (1) |
|---|---|---|---|
| Scoping | Given a vague goal, names the *smallest* thing they would ship first, with a clear test | Names a reasonable first step; might overshoot | Wants to redesign the whole system first |
| Iteration loop | Writes → tests → runs → adjusts → repeats, visibly | Has a working loop, just slower | Goes dark for 25 minutes, then produces a wall of code |
| Taste | Defends a non-obvious choice with one clean sentence | Has opinions but can't always articulate them | Has no opinions; defers to "what you want" |

**R:** Look at the size and shape of their recent commits. Small and frequent beats large and rare.
**S:** The screen prompt is specifically designed to test this. Note: did they ask clarifying questions? Did they pick a clean scope? Did they write a test? Did they leave a clean state?
**D:** Ask "what would you cut from BrowserControl right now?" — listen for trade-off reasoning, not just opinions.

---

## Scoring worksheet (copy per candidate)

```
Candidate: ___________________   Date: ___________   Stage: R / S / D

1. Python & asyncio           /5  × 25  = ____
2. Playwright intuition       /5  × 25  = ____
3. MCP / agent literacy       /5  × 15  = ____
4. OSS instinct & writing     /5  × 15  = ____
5. Velocity & taste           /5  × 20  = ____
                                       ─────
                                  Total: ____ /100

Decision:  Advance  Hold  Decline

One-line summary:
__________________________________________________________
```

## Calibration notes

- **Don't grade on background.** No points for "FAANG," no points lost for "self-taught." The signals above are signal-only.
- **Don't grade on style.** Code style is a conversation, not a score. Tabs vs spaces, `list[dict]` vs `Dict[str, Any]` — none of that affects the rubric.
- **Calibrate together.** After every 3 candidates, the founder reviews scores against the bar and re-anchors.
- **When in doubt, advance.** For a founding hire, a borderline-yes with a clear weakness is better than a borderline-no with strong surface area. The 90-min design chat is the tie-breaker.

---

*Maintained alongside [`founding-engineer.md`](founding-engineer.md) and [`founding-engineer-screen.md`](founding-engineer-screen.md). When the rubric changes, note the change at the bottom of this file.*
