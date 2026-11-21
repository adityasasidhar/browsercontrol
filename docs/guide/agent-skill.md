---
title: Agent skill
description: Install the BrowserControl skill, a playbook that teaches agents to drive the browser reliably, and the machine-readable docs agents can use.
---

# Agent skill

Connecting the MCP server tells an agent which tools exist. The **skill** teaches it how to use them well: that numbers expire after every action, that a cookie banner can swallow a click, that a missing number usually means "scroll". It is a Markdown playbook the agent loads only when a task involves a browser.

It's optional. BrowserControl works without it, but with it agents hit fewer stale IDs and retry the wrong element less often.

## Install it

The [Codex](/guide/clients#codex), [Claude Code](/guide/clients#claude-code), and [OpenCode 2](/guide/clients#opencode) plugins include the skill. To install it by hand in Claude Code:

::: code-group

```bash [This project]
mkdir -p .claude/skills/browsercontrol
curl -fsSL https://raw.githubusercontent.com/adityasasidhar/browsercontrol/main/skills/browsercontrol/SKILL.md \
  -o .claude/skills/browsercontrol/SKILL.md
```

```bash [All projects]
mkdir -p ~/.claude/skills/browsercontrol
curl -fsSL https://raw.githubusercontent.com/adityasasidhar/browsercontrol/main/skills/browsercontrol/SKILL.md \
  -o ~/.claude/skills/browsercontrol/SKILL.md
```

:::

Restart Claude Code and confirm with `/skills`. You can also call it directly with `/browsercontrol`.

**Other agents:** the file is plain Markdown with a short YAML header. Paste its body into whatever your client uses for standing instructions, such as a rules file or a system prompt.

## Why it costs almost nothing

Skills load in stages:

| Stage | What loads | When |
| --- | --- | --- |
| 1 | The `name` and one-line `description` | Every session, about one line |
| 2 | The body of `SKILL.md` | Only when a task needs a browser, or you type `/browsercontrol` |

On a task with no browser in it, the agent carries a single sentence.

## What's in it

- **The loop**, and why every action makes the previous screenshot useless.
- **Three rules** that prevent most failures: an ID lives for one screenshot, no number means hidden rather than absent, and the text map is ground truth.
- **How to choose a tool**: `find` versus scrolling, `act` versus single calls, extraction versus reading the page, `wait_for` versus fixed waits.
- **Behavior to rely on**: `type_text` replaces rather than appends, `check_checkbox` sets rather than toggles, settings like mocks stick until undone, full-page screenshots aren't annotated.
- **Recipes** for forms, debugging, responsive checks, multi-tab research, and recording.
- **Recovery**: a symptom-to-fix table.

Read it on [GitHub](https://github.com/adityasasidhar/browsercontrol/blob/main/skills/browsercontrol/SKILL.md).

## Docs for agents

This site is published in forms an agent can read directly:

| URL | What it is |
| --- | --- |
| [`/llms.txt`](/llms.txt){target="_blank"} | An index of every page with a one-line summary, following [llmstxt.org](https://llmstxt.org). |
| [`/llms-full.txt`](/llms-full.txt){target="_blank"} | All of the documentation in one file. |
| Any page + `.md` | That page as plain Markdown, for example [`/guide/quickstart.md`](/guide/quickstart.md){target="_blank"}. |
| [`/tools.json`](/tools.json){target="_blank"} | Every tool with its signature, parameters, and return type, generated from the server. |

Each page also has a **Copy page** button under its title, with options to view the Markdown or open the page in an AI assistant.
