---
title: Extract data
description: Pull tables, links, and arbitrary fields out of a page as JSON with extract_table, extract_links, and schema-based extract.
---

# Extract data

> Get every product on this page with its name, price, and link, as JSON.

```text
→ navigate_to("https://shop.test/keyboards")
→ extract({"products": [{"_selector": ".product", "name": "h3", "price": ".price", "url": "a@href"}]})
```

Reading data off a screenshot is slow and error-prone. The extraction tools return structured text instead, with no screenshot.

## Tables

```text
→ extract_table()
table #1: 2 row(s), 2 header(s)
[{"Name": "Apple", "Price": "1"}, {"Name": "Pear", "Price": "2"}]
```

- Pick a table by any element inside it, `extract_table(element_id=12)`, or by position, `extract_table(index=2)`.
- `output_format` is `json` (rows keyed by header), `markdown`, or `csv`.
- Works on HTML `<table>` (honoring `<thead>`, an all-`<th>` first row, and `colspan`) and on ARIA `role="table"` and `role="grid"` widgets.

## Links

```text
→ extract_links(contains="docs", limit=50)
```

Every link on the page, shadow DOM included, as `{text, href, visible}`, with absolute URLs and duplicates removed. `contains` filters by text or URL.

## Anything else: a schema

Describe the shape you want, using CSS selectors as values:

```text
→ extract({"title": "h1",
           "products": [{"_selector": ".product",
                         "name": "h3", "price": ".price", "url": "a@href"}]})
{
  "title": "Keyboards",
  "products": [
    {"name": "Halo 75", "price": "$129", "url": "https://shop.test/halo-75"},
    {"name": "Lumen TKL", "price": "$99", "url": "https://shop.test/lumen-tkl"}
  ]
}
```

| Value | Returns |
| --- | --- |
| `"h1"` | Text of the first match (a form field gives its value) |
| `"a@href"` | An attribute of the first match; `href` and `src` come back absolute |
| `"@href"` | An attribute of the scoped element itself |
| `[".tag"]` | Text of **every** match |
| `[{"_selector": ".card", …}]` | One object per match, fields relative to it |
| `{"_selector": "#main", …}` | One object, scoped to the first match |

Schema selectors run against the main document, not inside iframes or shadow roots. For those, use `get_text(id)` on numbered elements.

## Pages that load more as you scroll

Infinite feeds only render what's near the viewport. Scroll, extract, and repeat:

```text
→ scroll("down", "page")
→ extract({"posts": [{"_selector": "article", "title": "h2", "url": "a@href"}]})
```

Duplicates across passes are yours to merge.
