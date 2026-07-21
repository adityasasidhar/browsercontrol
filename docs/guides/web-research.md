# Web research

The classic "ask the agent a question about the web" loop. Three steps: search, read, summarize.

## What the agent does

> _"Find the Wikipedia article on Python and tell me who created it."_

```text
→ navigate_to("https://wikipedia.org")
→ type_text(2, "Python programming language")
→ press_key("Enter")
→ get_page_content()
→ "Python was created by Guido van Rossum, first released in 1991."
```

## Step by step

### 1. Navigate

```text
navigate_to("https://wikipedia.org")
```

BrowserControl returns an annotated screenshot and an element map. The search input is typically element `[2]` on Wikipedia's homepage.

### 2. Type and submit

```text
type_text(2, "Python programming language")
press_key("Enter")
```

`type_text` uses `element.fill()` for atomic input. After typing, press Enter to submit the search.

### 3. Read the result page

```text
get_page_content()
```

Returns the page as Markdown, with scripts and styles stripped. The 30 KB cap is plenty for most articles.

### 4. Extract the answer

The agent reads the Markdown response and produces the final answer.

## Variations

### Search results pages

If the search lands on a results page first, you may need to click a result before calling `get_page_content`:

```text
→ navigate_to("https://duckduckgo.com/?q=python+programming")
→ click(8)              # the first organic result
→ get_page_content()
```

### Reading a specific element

If you only want one paragraph (saves tokens), use `get_text`:

```text
→ click(8)              # expand the lead paragraph, or click a section
→ get_text(3)           # read a specific element
```

### Multi-page research

For "compare X and Y" style questions, see the [multi-tab research](multi-tab.md) guide.

## Tips

!!! tip "Use `get_page_info` to confirm"
    If the agent gets confused about which page it's on, call `get_page_info()` to dump the current URL and title.

!!! tip "Token costs"
    `get_page_content` returns up to 30 KB of Markdown. For very long articles, scroll to the section you want and use `get_text` on a specific element instead.

!!! tip "JS-rendered SPAs"
    Sites that load content via JS may need a `wait(1.0)` after navigation before `get_page_content` returns the rendered text.
