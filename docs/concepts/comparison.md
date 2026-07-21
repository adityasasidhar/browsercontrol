# How BrowserControl compares

Honest comparisons with the other browser-automation options in the MCP / agent ecosystem.

## TL;DR

| Capability | **BrowserControl** | Playwright MCP | Stagehand / Browser-Use | AgentQL |
|---|:-:|:-:|:-:|:-:|
| **Set of Marks** (numbered boxes) | ✅ | ❌ text-tree only | ❌ | ❌ |
| **Shadow DOM traversal** | ✅ recursive | ⚠️ partial | ⚠️ varies | ⚠️ varies |
| **Same-origin iframe support** | ✅ with offset coords | ⚠️ basic | ⚠️ varies | ❌ |
| **Native `set_input_files` upload** | ✅ | ⚠️ manual | ❌ | ❌ |
| **Built-in devtools** (console/network/errors/perf) | ✅ 11 tools | ⚠️ partial | ❌ | ❌ |
| **Multi-tab control** | ✅ | ⚠️ implicit | ⚠️ varies | ❌ |
| **True persistent profile** | ✅ `launch_persistent_context` | ⚠️ | ❌ | ❌ |
| **No external LLM API required** | ✅ | ✅ | ❌ needs API key | ❌ cloud |
| **Runs 100% locally / offline** | ✅ | ✅ | ❌ | ❌ |
| **Cost per 1k actions** | **$0** | $0 | API spend | API spend |

## Playwright MCP

[Playwright's own MCP server](https://github.com/microsoft/playwright-mcp) is excellent if you're fine with the accessibility-tree approach. It exposes the page's accessibility tree as a textual representation, and the model picks elements from that.

**Trade-offs:**

- ✅ Battle-tested, Microsoft-backed.
- ✅ Stable selectors when the page has good a11y.
- ❌ No vision — text-only.
- ❌ Selectors drift when the page changes.
- ❌ No built-in devtools.

**When to pick Playwright MCP:** your pages have good accessibility markup and you want a Microsoft-supported tool.

## Stagehand / Browser-Use

[Stagehand](https://stagehand.dev) and [Browser-Use](https://browser-use.com) put an LLM in the loop with browser automation. The LLM decides what to do at each step, often using vision.

**Trade-offs:**

- ✅ State-of-the-art performance on benchmarks.
- ✅ Self-healing when pages change.
- ❌ Requires an LLM API key (cost + privacy).
- ❌ Adds latency (extra LLM call per step).
- ❌ Not great for production automation (latency + cost).

**When to pick Stagehand / Browser-Use:** you want the highest benchmark scores and don't care about per-action cost.

## AgentQL

[AgentQL](https://agentql.com) is a query language for the web — you write a query that describes the data you want, and AgentQL extracts it.

**Trade-offs:**

- ✅ Structured extraction is its strength.
- ❌ Cloud-only — sends your browsing to their servers.
- ❌ Per-query pricing.
- ❌ Not a general browser automation tool.

**When to pick AgentQL:** you want to extract structured data from many pages and don't mind sending them to a cloud service.

## BrowserControl's niche

BrowserControl is for the case where you want:

1. **Vision + text together.** The model picks the cheaper representation per step.
2. **Zero external dependencies.** No API keys, no cloud, no per-action costs.
3. **Full devtools built-in.** Console, network, errors, performance — no second tool.
4. **Modern web app support.** Shadow DOM, iframes, persistent profiles.

It's the right choice if you're running an MCP server in a privacy-sensitive context (your data stays on your machine), or if you're integrating browser automation into an agent and don't want to manage another cloud bill.

## See also

- **[Set of Marks](set-of-marks.md)** — the technique that powers BrowserControl
- **[Architecture](architecture.md)** — how the components fit together
