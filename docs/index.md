---
hide:
  - navigation
  - toc
---

<div class="hero" markdown>
<div class="hero-inner" markdown>

# BrowserControl

**Give your AI agent real browser superpowers.**

Vision-first browser automation for any MCP-compatible AI agent — local, private, and zero-cost.

[Get started :material-rocket-launch:](getting-started/index.md){ .md-button .md-button--primary }
[Why BrowserControl?](concepts/index.md){ .md-button }

</div>
</div>

<div class="badges" markdown>

[![PyPI](https://img.shields.io/pypi/v/browsercontrol?color=blue&label=PyPI)](https://pypi.org/project/browsercontrol/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-3776ab.svg?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![MCP Compatible](https://img.shields.io/badge/MCP-compatible-7c3aed.svg)](https://modelcontextprotocol.io/)
[![CI](https://img.shields.io/github/actions/workflow/status/adityasasidhar/browsercontrol/ci.yml?branch=main&label=CI)](https://github.com/adityasasidhar/browsercontrol/actions)
[![Stars](https://img.shields.io/github/stars/adityasasidhar/browsercontrol?style=social)](https://github.com/adityasasidhar/browsercontrol/stargazers)

</div>

## What it is

BrowserControl is an [MCP](https://modelcontextprotocol.io) server that gives your AI agent a real browser it can **see**, **click**, **type**, and **debug** — using a vision-first approach based on the **Set of Marks (SoM)** pattern.

Instead of fragile CSS selectors, XPath, or DOM trees, the agent sees an annotated screenshot with **numbered red boxes** over every interactive element, then just calls:

```text
click(5)                    →  clicks the 5th element
type_text(3, "hello world") →  types into the 3rd element
upload_file(7, "/path.pdf") →  uploads via the native browser input
```

No selectors to guess. No selectors to break when the page changes. **Just point at numbers.**

## How it looks

Every tool that interacts with the page returns an **annotated screenshot** plus a textual element map:

```
┌─────────────────────────────────────────────────┐
│  GitHub                          [Sign in]      │
├─────────────────────────────────────────────────┤
│                                                 │
│   ┌──────────────────────┐    ┌──────────────┐  │
│   │ 1  🔍 Search…        │    │ 2  Pulls     │  │
│   └──────────────────────┘    │ 3  Issues    │  │
│                               │ 4  Codespace │  │
│   ┌───────────────────────┐   └──────────────┘  │
│   │ 5  Sign in            │                     │
│   └───────────────────────┘                     │
└─────────────────────────────────────────────────┘

Found 5 interactive elements:
  [1] input - Search or jump to...
  [2] a - Pulls
  [3] a - Issues
  [4] a - Codespaces
  [5] button - Sign in
```

The model receives the image *and* the list, so it can either reason over the pixels or read the text — whichever is cheaper.

## Why BrowserControl?

<div class="grid cards" markdown>

- :material-eye-outline:{ .lg .middle } **Vision-first, selector-free**

    ---

    Numbered red boxes on every interactive element. The agent picks a number. **No selectors, ever** — and zero hallucinated `div.flex-container > button.btn-primary:nth-child(3)`.

- :material-layers-triple:{ .lg .middle } **Shadow DOM & iframe aware**

    ---

    Recursively descends into open shadow roots and same-origin iframes (with proper coordinate offsets). Modern web apps just work.

- :material-database:{ .lg .middle } **True persistent sessions**

    ---

    Uses `launch_persistent_context`. Cookies, `localStorage`, login state, and history all survive restarts. **Log in once.**

- :material-tools:{ .lg .middle } **Built-in devtools**

    ---

    Console logs, network requests (with timing), JS errors, page performance, element inspection, computed styles. No second tool needed.

- :material-cloud-off-outline:{ .lg .middle } **100% local & private**

    ---

    No LLM API key. No cloud. No telemetry. No usage cap. Your browsing stays on your machine.

- :material-currency-usd-off:{ .lg .middle } **Zero marginal cost**

    ---

    Runs on your hardware. **$0 per 1,000 actions** — no API spend, no per-action fees, no surprise invoices.

</div>

## Install in 30 seconds

=== "pip"

    ```bash
    pip install browsercontrol
    ```

=== "uv"

    ```bash
    uv add browsercontrol
    ```

=== "pipx"

    ```bash
    pipx install browsercontrol
    ```

Chromium auto-installs on first run. If it fails for any reason, run `python -m playwright install chromium` once and you're set.

## Next steps

<div class="grid cards" markdown>

-   :material-rocket-launch:{ .lg .middle } **[Getting started](getting-started/index.md)**

    ---

    Install, run, and connect BrowserControl to your AI in under five minutes.

-   :material-tools:{ .lg .middle } **[Tool reference](tools/index.md)**

    ---

    Every MCP tool, every parameter, organized by category.

-   :material-book-open-variant:{ .lg .middle } **[Guides](guides/index.md)**

    ---

    Real-world patterns: research, debugging, recording, form filling, multi-tab workflows.

-   :material-graph-outline:{ .lg .middle } **[Concepts](concepts/index.md)**

    ---

    How Set of Marks works, the action loop, and why it beats selectors.

</div>
