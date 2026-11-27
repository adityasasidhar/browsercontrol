---
title: FAQ
description: Short answers to common questions about BrowserControl's cost, privacy, models, browsers, and limits.
---

# FAQ

## Does BrowserControl call an AI model?

No. It's a tool server: your client's model decides what to do, and BrowserControl does it. It needs no API key and adds no per-action cost.

## Does my browsing leave my machine?

Not because of BrowserControl. The browser, its profile, captured traffic, recordings, and downloads all stay local. What does leave is what your MCP client sends to its model: tool results, including screenshots and page text. Treat pages the agent visits the way you'd treat anything else you paste into a chat.

## Which models work best?

Any model your client supports can use the text element list, but BrowserControl is designed for models that can see images, since each result includes the annotated screenshot.

## Can it use Firefox or Safari?

No, it drives Chromium or Chrome. It can [emulate phones and tablets](/recipes/responsive) in Chromium, but it can't run Firefox's or Safari's engines.

## Can it see my everyday Chrome tabs?

Only if you start Chrome with remote debugging and attach with `connect_to_chrome`. Even then it opens its own tab and doesn't touch yours unless asked. By default it uses a separate browser with its own profile.

## Why do numbers change after every action?

Because the page might have changed. Each screenshot is numbered from scratch, so a number always means what you see right now. See [Set of Marks](/concepts/set-of-marks).

## Can several agents use it at once?

Yes. Run it [over HTTP](/guide/http) and connect each client to the same URL. Add `--isolate-clients`, and give each agent its own token in [`BROWSER_AUTH_TOKENS`](/guide/http#per-client-tokens), so each agent gets its own cookies, tabs, and traffic.

## Can it solve CAPTCHAs or get past bot protection?

No, and it isn't built to. If a site challenges the agent, sign in yourself through [your own Chrome](/recipes/your-chrome), or use a different source.

## Where does it keep files?

Under `~/.browsercontrol/`: the profile, recordings, snapshots, downloads, and generated tests. Each location can be moved; see [Configuration](/reference/configuration#paths).

## How do I see what the agent is doing?

The browser window is visible by default (set `BROWSER_HEADLESS=true` to hide it). You can also record a [trace](/recipes/record-tests) and replay it afterwards.
