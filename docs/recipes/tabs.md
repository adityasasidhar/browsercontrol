---
title: Work across tabs
description: Open several pages in tabs, switch between them, and compare what they say.
---

# Work across tabs

> Compare the pricing pages of two products and tell me which has the cheaper team plan.

```text
→ create_tab("https://product-a.example/pricing")
→ create_tab("https://product-b.example/pricing")
→ list_tabs()
→ switch_tab(1)
→ extract_table()
→ switch_tab(2)
→ extract_table()
```

<div class="steps">

### Open tabs

`create_tab(url)` opens a tab, switches to it, and returns its screenshot. Without a URL it opens a blank tab.

### See what's open

```text
→ list_tabs()
Open Tabs:
  [0] Hacker News - https://news.ycombinator.com
  [1] Pricing · Product A - https://product-a.example/pricing
* [2] Pricing · Product B - https://product-b.example/pricing
```

Tabs are numbered from 0, `*` marks the active one, and `list_tabs` returns text only, so it's cheap.

### Switch and read

`switch_tab(index)` focuses a tab and returns a fresh screenshot of it. Each tab keeps its own element map, so a number from tab 1 never resolves against tab 2.

</div>

## Good to know

- **Tabs share a session.** Cookies and storage are shared, so signing in on one tab signs in the others. For a separate user, use [`create_session`](/concepts/sessions#isolated-sessions).
- **Indexes shift.** Closing tab 0 makes tab 1 the new tab 0. Call `list_tabs()` again after closing.
- **Closing the active tab** switches to another open tab automatically.
- **Popups count.** A link that opens a new window adds a tab. `list_tabs()` shows it.
