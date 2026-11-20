---
hide:
  - navigation
  - toc
  - footer
---

<section class="bc-hero" markdown>

<div class="bc-hero-copy" markdown>

# Browser automation for AI agents

BrowserControl is a local MCP server that gives your AI client a Chromium browser.
It numbers controls in screenshots so your agent can click, type, and navigate
using the page it sees.

[Get started](getting-started/index.md){ .md-button .md-button--primary }
[Browse tools](tools/index.md){ .md-button }

</div>

<figure class="bc-example" markdown>

![A Chromium screenshot of a web form with numbered red boxes around its fields and Submit button](assets/images/annotated-web-form.webp){ width="822" height="336" }

<figcaption markdown>

BrowserControl marks the form’s controls. In this screenshot, `click(2)` presses Submit.

</figcaption>
</figure>

</section>

## Set up BrowserControl

<div class="grid cards bc-setup" markdown>

-   **1. [Install](getting-started/installation.md)**

    Install the server. It finds a compatible browser or downloads Chromium on first launch.

-   **2. [Connect an MCP client](getting-started/connect-your-ai.md)**

    Add BrowserControl to Claude, Cursor, VS Code, or another client with stdio support.

-   **3. [Run your first session](getting-started/first-session.md)**

    Ask your agent to fill a demo form and check the result.

</div>

## What you can do

<div class="grid cards" markdown>

-   :material-cursor-default-click-outline: **[Act on what it sees](tools/interaction.md)**

    Click, type, drag, and `find("text")` anywhere on the page, iframes and
    shadow DOM included. Batch steps with `act`.

-   :material-google-chrome: **[Use your own Chrome](guides/use-your-chrome.md)**

    Attach to the Chrome you're signed in to, or open isolated sessions for a
    second user.

-   :material-table-arrow-right: **[Extract data](tools/extraction.md)**

    Read pages as Markdown, or pull tables, links, and fields as JSON.

-   :material-bug-outline: **[Debug a web app](guides/debug-web-app.md)**

    Console logs, request headers and bodies, page errors, and HAR export.

-   :material-test-tube: **[Test edge states](guides/mock-apis.md)**

    Mock API responses, throttle the network, and emulate devices, timezones,
    and dark mode.

-   :material-record-circle-outline: **[Record and export tests](guides/record-tests.md)**

    Save Playwright traces and turn the session into a runnable Playwright test.

</div>

## Find what you need

<div class="grid cards bc-paths" markdown>

-   :material-book-open-variant-outline: **[Tool reference](tools/index.md)**

    Look up tool arguments, defaults, and examples.

-   :material-map-outline: **[Guides](guides/index.md)**

    Fill forms, inspect network requests, and record a browser session.

-   :material-eye-outline: **[Set of Marks](concepts/set-of-marks.md)**

    Learn how element numbers work and when they change.

-   :material-cog-outline: **[Configuration](configuration.md)**

    Set the viewport, browser profile, settle timeout, transport, and more.

</div>

[Fix setup or browser issues](troubleshooting.md)
