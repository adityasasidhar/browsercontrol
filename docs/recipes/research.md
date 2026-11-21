---
title: Research a question
description: Use BrowserControl to search a site, open the right result, read it efficiently, and answer with a source.
---

# Research a question

> Find who created the Python programming language using Wikipedia, and give me the source URL.

```text
→ navigate_to("https://en.wikipedia.org")
→ type_text(4, "Python programming language")
→ press_key("Enter")
→ find("Python (programming language)", role="link")
→ click(9)
→ get_page_content()
→ get_page_info()
```

<div class="steps">

### Search

Open the site, type into its search field, and submit with `press_key("Enter")` (or click the search button). If the site has a search URL, going straight there is faster: `navigate_to("https://en.wikipedia.org/w/index.php?search=python")`.

### Pick the result

Results pages are crowded. Rather than scanning the screenshot, let `find` locate the result by its text. It scrolls there and reports the number to click:

```text
→ find("Python (programming language)", role="link")
Found 1 match(es) for link 'Python (programming language)'; scrolled to match 1.
  1. link 'Python (programming language)' -> element [9]  <- scrolled here
```

### Read

Choose the cheapest way to read:

| You need | Use |
| --- | --- |
| The article's text | `get_page_content()`: the page as Markdown, up to 30,000 characters |
| One paragraph or cell | `get_text(id)`: one element's full text |
| Every link on the page | `extract_links()` |
| A table | `extract_table()` |

### Cite

`get_page_info()` returns the current URL and title for the answer.

</div>

::: tip Long pages
`get_page_content()` cuts off at 30,000 characters. For a long article, `find` the section heading first, then read the elements you need with `get_text`.
:::

Comparing several sources at once? See [Work across tabs](/recipes/tabs).
