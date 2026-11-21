---
title: How it compares
description: How BrowserControl's numbered-screenshot approach differs from accessibility-tree servers, LLM-driven browser frameworks, and pixel-level computer use.
---

# How it compares

There are several good ways to give an agent a browser. They differ mostly in **what the model sees** and **who decides the next step**.

## Four approaches

| Approach | The model sees | The model acts by | Examples |
| --- | --- | --- | --- |
| **Numbered screenshots** | A screenshot with numbered boxes, plus the same list as text | Naming a number: `click(7)` | BrowserControl |
| **Accessibility snapshots** | A text tree of the page's roles and names, with references | Naming a reference from the tree | Playwright MCP |
| **Framework with its own LLM** | Whatever the framework shows its internal model | Natural-language instructions the framework turns into actions | Browser Use, Stagehand |
| **Pixels and coordinates** | A plain screenshot | Clicking at `x, y` | Computer-use style agents |

## Numbered screenshots

**Strengths**

- The model gets a picture *and* precise targets. Layout, color, and state are visible; icon-only buttons and input types are named in the list.
- It can't invent a target, since it can only pick a number that exists. Out-of-date numbers are refused rather than applied to whatever moved in.
- What the model sees is what a user sees: elements covered by a modal or overlay get no number.

**Trade-offs**

- Each step returns an image, which costs more tokens than a short text snapshot. The text list helps a text-only model, but the approach is designed for vision models.
- Only what's on screen is numbered, so long pages need `find` or scrolling.

## Accessibility snapshots

Servers like [Playwright MCP](https://github.com/microsoft/playwright-mcp) describe the page as a tree of roles and names. On well-built, accessible sites this is precise and compact, and it works with models that can't see images. It reaches iframes and shadow DOM too, and costs far fewer tokens per step than a screenshot. The model gets no picture of layout or visual state.

**Pick it when** token cost matters most, your model is text-only, or the task doesn't depend on how the page looks.

## Frameworks with their own LLM

Libraries such as [Browser Use](https://browser-use.com) and [Stagehand](https://stagehand.dev) put a model inside the automation layer: you describe a goal or step in words, and the framework decides what to click. That's convenient, but every step calls a model behind the scenes, which brings its own API key, latency, and cost.

**Pick it when** you're building an automation in code and want the framework to plan the steps.

## Pixels and coordinates

Computer-use agents click at coordinates on a plain screenshot. It works on anything, including canvases and native apps, but the model must locate targets precisely by itself, which is where most mistakes happen. BrowserControl keeps [`click_at(x, y)`](/reference/interaction#click_at) for the cases where nothing has a number.

## Where BrowserControl fits

Choose it when you want:

- **Vision and text together**, with targets the model can't get wrong by guessing.
- **Everything local.** BrowserControl calls no model and needs no API key. The browser, its profile, and its captured traffic stay on your machine.
- **A full toolbox** in one server: debugging, network mocking, emulation, recording, and test export, alongside the clicks.
- **Your real browser**: a persistent logged-in profile, or your own Chrome attached over CDP.
- **To see the page**: layout and visual bugs, mobile and dark-mode checks, and UIs where the picture matters.
