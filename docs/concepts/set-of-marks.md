# Set of Marks (SoM)

**Set of Marks** (SoM) is a visual prompting technique where you draw numbered labels on top of an image to make it easier for a vision-language model to refer to specific parts. BrowserControl uses SoM for every interactive element on the page.

## What it looks like

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

Every interactive element on the page is overlaid with a numbered red box, and the same elements are returned as a textual list.

## Why it beats selectors

| | SoM | CSS selectors | XPath | Accessibility tree |
|---|---|---|---|---|
| **Survives redesigns** | ✅ | ❌ | ❌ | ⚠️ partial |
| **No hallucinated values** | ✅ (pick a number) | ❌ (model invents selectors) | ❌ | ⚠️ |
| **Tiny tokens** | ✅ (~50 bytes/element) | ❌ | ❌ | ⚠️ |
| **Vision + text** | ✅ | ❌ text-only | ❌ | ❌ text-only |
| **Shadow DOM** | ✅ recursive | ⚠️ | ⚠️ | ⚠️ |
| **iframes** | ✅ with offsets | ⚠️ | ⚠️ | ⚠️ |

### The selector problem

CSS selectors and XPath were designed for **humans writing tests**. They assume the author can inspect the DOM and pick a stable path. AI agents don't have that context — they hallucinate `div.flex-container > button.btn-primary:nth-child(3)` and then have to debug when it doesn't work.

### The token problem

A full DOM tree for a moderately complex page is ~50 KB. A SoM element list is ~1 KB — **50× cheaper to send to the model**.

### The drift problem

When the site gets redesigned, CSS selectors break. SoM numbers don't — they point at pixels, which don't change unless the visual layout does.

## How BrowserControl implements SoM

1. **Detect** interactive elements (`<a>`, `<button>`, `<input>`, `<select>`, `<textarea>`, `[onclick]`, `[role=button]`, etc.).
2. **Recurse** into open shadow roots and same-origin iframes with coordinate offset compensation.
3. **Filter** out elements that are off-screen, hidden, or have zero size.
4. **Annotate** the screenshot with numbered red boxes drawn at each element's bounding box.
5. **Return** both the annotated image and the textual element map.

The annotation is done in Python with Pillow — no JS injection, no DOM mutation. The page itself is never modified.

## Resolution: element ↔ pixel

When the agent calls `click(5)`, BrowserControl doesn't click at the literal center of the box. It does:

```js
document.elementFromPoint(elem.centerX, elem.centerY)
```

This returns the **actual** DOM element at those coordinates, which is what the click hits. This is what lets the click get through sticky headers, modals, and overlays that would otherwise fool a coordinate-only clicker.

## When SoM is not enough

For pages with hundreds of interactive elements (Google search results, infinite-scroll feeds), the element map gets crowded. Strategies:

- **Scroll first** — call `scroll(direction)` to bring different parts of the page into view, then re-screenshot.
- **Use `get_text`** — read text from a specific element instead of trying to pick from a noisy screenshot.
- **Use `run_javascript`** — extract structured data directly from the DOM when you know what you want.

## See also

- **[Architecture](architecture.md)** — how SoM fits into the action loop
- [Original SoM paper](https://arxiv.org/abs/2304.08242) — the research behind the technique
