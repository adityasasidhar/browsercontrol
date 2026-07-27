# Agent skill

Connecting the MCP server tells your agent **which tools exist**. It doesn't tell
it how to use them well — that the element numbers expire after every action,
that a cookie banner will swallow a click, that a missing number usually means
"scroll". BrowserControl ships that knowledge as a **skill**: a markdown playbook
your agent loads on demand, only when it's actually driving a browser.

!!! info "This is optional"

    BrowserControl works without it. The skill makes agents noticeably more
    reliable — fewer stale-ID errors, fewer retries on the same wrong element.

## Install it

The skill lives at
[`skills/browsercontrol/SKILL.md`](https://github.com/adityasasidhar/browsercontrol/blob/main/skills/browsercontrol/SKILL.md)
in the repository.

=== "Claude Code — this project only"

    Checked into the repo, shared with everyone who clones it:

    ```bash
    mkdir -p .claude/skills/browsercontrol
    curl -fsSL https://raw.githubusercontent.com/adityasasidhar/browsercontrol/main/skills/browsercontrol/SKILL.md \
      -o .claude/skills/browsercontrol/SKILL.md
    ```

=== "Claude Code — all your projects"

    ```bash
    mkdir -p ~/.claude/skills/browsercontrol
    curl -fsSL https://raw.githubusercontent.com/adityasasidhar/browsercontrol/main/skills/browsercontrol/SKILL.md \
      -o ~/.claude/skills/browsercontrol/SKILL.md
    ```

=== "Other agents"

    The file is plain markdown with YAML frontmatter. Paste the body into
    whatever your client uses for persistent instructions — a system prompt, a
    rules file, a custom instruction block.

Restart your client. In Claude Code, confirm with `/skills`; you can also invoke
it directly with `/browsercontrol`.

## How it works

Skills use **progressive disclosure**, which is why adding one costs almost
nothing:

| Tier | What loads | When |
|---|---|---|
| 1 | `name` + `description` from the frontmatter | Every session — about one line |
| 2 | The `SKILL.md` body | Only when the agent judges it relevant, or you type `/browsercontrol` |
| 3 | Any files the body points to | Only if the agent follows the pointer |

So the agent permanently carries one sentence — *"drive a browser via numbered
screenshots; use when the task needs a live browser"* — and pulls in the full
playbook the moment a task matches. On a task with no browser in it, you pay
nothing.

## What's in it

- The core loop, and why every action invalidates the previous screenshot
- The three rules that prevent most failures: ephemeral IDs, viewport-only
  marking, read the text summary
- Behaviors that surprise agents — `type_text` replaces rather than appends,
  clicks land on whatever is topmost at the coordinate, cross-origin iframes are
  never marked, `full_page=True` silently disables annotation
- Recipes for forms, debugging, responsive checks, multi-tab research, recording
- A symptom → fix recovery table

## Machine-readable docs

The documentation site also publishes an
[`llms.txt`](https://adityasasidhar.github.io/browsercontrol/llms.txt) at its
root, following the [llmstxt.org](https://llmstxt.org) convention: a short
project summary plus a curated, annotated link map of every page. Point an agent
at that URL when you want it to find its own way around these docs.

## See also

- **[Set of Marks (SoM)](../concepts/set-of-marks.md)** — why the numbers work the way they do
- **[Connect your AI](connect-your-ai.md)** — wiring up the MCP server itself
- **[Tool reference](../tools/index.md)** — every tool, with signatures
