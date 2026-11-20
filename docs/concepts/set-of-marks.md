---
title: Set of Marks
description: How BrowserControl numbers what an agent can use, how long a number stays valid, and what happens when it goes stale.
---

# Set of Marks

**Set of Marks** is a way of prompting a vision model: draw a numbered box around each thing it can act on, and let it answer with a number. BrowserControl uses it as its whole interface. Each annotated screenshot outlines every usable control, and the same numbers come back as a text list.

![A demo web form with numbered boxes on every field and button](/images/annotated-web-form.webp)

An agent looking at this calls `type_text(3, "Hello")` for the text input and, after reading the new map, `click(2)` for Submit.

The technique comes from the paper [Set-of-Mark Prompting Unleashes Extraordinary Visual Grounding in GPT-4V](https://arxiv.org/abs/2310.11441).

## What gets a number

An element is numbered when it is **interactive**, **in the viewport**, and **not covered**.

**Interactive** means any of:

- links, buttons, inputs (except hidden ones), selects, textareas, `summary`, `label[for]`
- elements with a role such as `button`, `link`, `tab`, `menuitem`, `checkbox`, `radio`, `switch`, `option`, `combobox`, or `textbox`
- `contenteditable` regions, `[onclick]`, and focusable `[tabindex]` elements
- elements that start a `cursor: pointer` area, which catches framework click handlers that leave no attribute behind

**In the viewport** means at least partly on screen. Off-screen controls get no number until you scroll to them or `find` them.

**Not covered** means the element itself is what you would click at that spot. A control under a cookie banner, modal, or sticky header gets no number. There is one exception: checkboxes, radios, and file inputs that a site makes transparent and replaces with a styled stand-in are still numbered, because they still work.

Detection runs in **every frame**, cross-origin iframes included, and descends into **open shadow roots**. **Disabled** controls are numbered too, drawn grey, and listed as `(disabled)`, so the agent can see that a button exists but needs something first.

## A number lives for one screenshot

Every annotated screenshot rebuilds the map from scratch: every click, typed value, scroll, navigation, tab switch, and `screenshot()` call. Number 7 before a click can be a different element, or nothing, after it.

The rule for agents is short: **read the newest map before every action that takes an ID.** The one exception is [`act`](/reference/interaction#act), where every ID in the batch refers to the map from before the call.

Maps are kept per tab, so an ID from one tab never resolves against another.

## Stale IDs {#stale-ids}

When the agent passes a number, BrowserControl finds that element again by a tag it placed on it during the screenshot, using a locator scoped to the element's own frame. Before acting it checks that the element is still the one the screenshot showed. It refuses when the element has:

- been removed from the page, or its frame has gone
- become hidden
- changed content (a framework recycled the node for something else)
- been duplicated, so the tag is ambiguous
- moved more than 3 pixels and settled somewhere new (an element still animating is accepted)

A refusal returns an error and a fresh screenshot to choose from:

```text
Error: Element 7 is stale (it moved). The page changed since the last
screenshot; use the IDs in the fresh one below.

Found 18 interactive elements:
  ...
```

An unknown number gets `Error: Element 42 not found. Valid IDs: [1, 2, 3, …]`. In both cases nothing was clicked, so it's safe to retry with a number from the new map.

## When the control you want has no number

| Situation | What to do |
| --- | --- |
| It's below the fold and you know its text | `find("Delete account")` searches the whole page, iframes and shadow DOM included, scrolls to it, and returns its number. |
| You're exploring | `scroll("down")` and read the new map. |
| You can see it, but it has no number | Something covers it. Close the banner or modal first. |
| It's a canvas or a map with no elements | `click_at(x, y)` with coordinates from the screenshot. |

## Crowded pages

On a page with hundreds of controls, picking from the screenshot gets noisy. Some ways around that:

- **Search instead of scanning.** `find("Add to cart", role="button")` lists every match with its number and skips text that isn't a button.
- **Batch.** Once you have the numbers you need, `act` runs the steps against one map in a single call.
- **Extract instead of reading.** [`extract_table`, `extract_links`, and `extract`](/reference/extraction) return structured data without picking elements at all.
- **Read one element.** `get_text(id)` returns an element's full, current text.

## Why not selectors?

Selectors are written by the model, so they can be wrong, and they break when a site changes its markup. Accessibility trees are precise on well-built sites, but they're long and give the model no picture of the page. Numbers on a screenshot give the model something it can see and something it can't get wrong by inventing: it can only pick a number that exists. See [How it compares](/concepts/comparison).
