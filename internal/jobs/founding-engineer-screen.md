# Founding Engineer — 30-Minute Screen Prompt

**Format:** Live pair-programming, screen-shared, in a coding tool the candidate already uses. 30 minutes hard stop.
**Pairing partner:** Founder.
**Calibrated to:** the **"Cookie import/export (Netscape format)"** item in the *Good first contributions* list in the BrowserControl README. This was chosen because it tests Python, `asyncio`, file-format handling, test discipline, and API design instincts — without needing a browser binary.

The full rubric this screen feeds into is in [`founding-engineer-rubric.md`](founding-engineer-rubric.md). This file is just the prompt.

---

## Pre-screen setup (founder, 5 min before)

- Fork `adityasasidhar/browsercontrol` into a private repo under the founder's org.
- Add the candidate as a collaborator.
- Open `browsercontrol/tools/devtools.py` and `tests/test_devtools.py` in the IDE.
- Have the README's "Cookie import/export" item visible in the chat.
- Open the [Netscape cookie file format spec](https://curl.se/docs/http-cookies.html) in a browser tab.

## The prompt (read this aloud at minute 0)

> "BrowserControl already has `get_cookies`, `set_cookie`, `delete_cookie`, and `clear_cookies` in `browsercontrol/tools/devtools.py`. The README lists cookie import/export as a 'good first contribution'. In the next 30 minutes, I'd like you to design and *partially* implement the **export** half of that feature — enough that we can talk through the import half from a clean design.
>
> Three constraints:
>
> 1. **The export must follow the Netscape cookie file format** — that's the format `curl`, `wget`, and most browser cookie importers understand. Spec is in your second tab.
> 2. **You don't need to run a browser.** Write the code against the existing `mock_page` / `mock_browser_manager` fixtures in `tests/conftest.py`. We are grading design and code, not browser execution.
> 3. **You have 30 minutes.** At minute 25, stop coding and spend 5 minutes walking me through what you'd do for the `import` half and what edge cases you'd handle.
>
> Two things I want to see, in order of importance:
>
> - **A clear, narrow scope.** Pick the smallest useful slice. Don't redesign the existing `set_cookie` tool. Don't add new env vars.
> - **One good test.** A test that proves your parser handles a real Netscape-format file, including the `#HttpOnly_` prefix on the cookie name. You don't need full coverage — one good test is better than five rushed ones.
>
> Pick whatever name you want for the new tool — we'll discuss whether to call it `export_cookies`, `save_cookies`, or something else when you walk me through it. Go."

## What to watch for (founder scoring sheet)

| Behavior | What it signals |
|---|---|
| Asks a clarifying question in the first 5 minutes ("Which cookies — current page or all origins the browser has visited?") | **Scoping instinct, +1 to criterion 5** |
| Reaches for `dataclasses.dataclass` or a `TypedDict` for the parsed row | **Type discipline, +1 to criterion 1** |
| Writes the test *before* or alongside the parser, not at the end | **Iteration loop, +1 to criterion 5** |
| Quotes any part of the Netscape spec from memory | **MCP literacy / spec discipline, +1 to criterion 3** |
| Notices the `#HttpOnly_` prefix and the `domain` "include subdomains" flag | **Browser-automation depth, +1 to criterion 2** |
| Picks a scope, says it out loud, then ships within it | **Taste & velocity, +1 to criterion 5** |
| Stops at 25 minutes and writes a clear walkthrough of the import half | **Communication, +1 to criterion 4** |

### Soft fails (signals to pause and probe harder)

- Rewrites the existing cookie tools instead of adding a new one.
- Adds a new dependency to `pyproject.toml` for a 30-line feature.
- Spends 20 minutes on the readme and 5 minutes on the code.
- Tests only the happy path and refuses to acknowledge the `#HttpOnly_` case when asked.

### Hard fails (decline)

- Cannot produce runnable code in 30 minutes.
- Cannot read or write a Python function with type hints in this codebase.
- Talks over the partner, refuses to walk through the code at minute 25.
- Uses a language other than Python without checking first.

## Walkthrough questions (minute 25–30, in this order)

1. "Walk me through what you built. What's the function signature, and what's the test asserting?"
2. "What would the **import** side look like? Same shape, or different?"
3. "What's the *one* edge case you'd want to test for import that you couldn't fit in this 30 minutes?"
4. "If you had a week, what's the next thing you'd build on top of this?"

Question 4 is the most important — the answer reveals how they think about scope and what they'd prioritize as the founding engineer.

## After the screen (founder, 10 min after)

- Fill in the screening rubric sheet for criterion 2 (Playwright intuition — they didn't touch a browser, but the *frame* they took to the spec tells you a lot) and criterion 5 (velocity & taste).
- Write a 3-sentence summary in the candidate tracker.
- Send the candidate a thank-you note within 24 hours, regardless of outcome.

## Why this prompt and not one of the others

We considered all of the README's "good first contributions":

| Contribution | Why we didn't pick it for the screen |
|---|---|
| Firefox / WebKit support | Requires a Playwright binary install; can't be graded in 30 min without a browser. |
| DOM diffing | Too open-ended; framing the problem *is* the test. Better suited to the 90-min design chat. |
| Accessibility audit tools | Needs a real page to demonstrate. Out of scope for a no-browser screen. |
| Mobile emulation presets | Too narrow — mostly a config tweak. Doesn't surface API design instincts. |
| `--record-video` MP4 output | Same as Firefox — needs the browser. |
| Network request blocking / mocking | Strong runner-up; chosen as the **alternative prompt** below. |

**Alternative prompt (use if the candidate is coming from a network-engineering background):**

> "Add an MCP tool that blocks all requests matching a glob pattern. 30 minutes. Don't touch a browser. Test against the mocked page context. Walk me through how you'd expose this as `block_requests(['*.doubleclick.net', '*/analytics/*'])`."

It's the same shape — narrow scope, one good test, walkthrough at minute 25 — and it tests different instincts (regex/glob thinking, Playwright route API knowledge).

---

*Maintained alongside [`founding-engineer.md`](founding-engineer.md) and [`founding-engineer-rubric.md`](founding-engineer-rubric.md). If the screen prompt changes, version it.*
