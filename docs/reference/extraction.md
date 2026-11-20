---
title: Extraction
description: Tables, links, and schema-driven fields as JSON, with no screenshot.
---

# Extraction

Structured data out of the page. These tools return text only.

| Tool | Does | Returns |
| --- | --- | --- |
| [`extract_table`](#extract_table) | Extract a table (HTML `<table>` or ARIA table/grid) as structured data. | text |
| [`extract_links`](#extract_links) | List the page's links as JSON: text, absolute href, and whether each is visible. | text |
| [`extract`](#extract) | Extract structured JSON from the page with a selector schema. | text |

## `extract_table` {#extract_table}

Extract a table (HTML `<table>` or ARIA table/grid) as structured data.

```python
extract_table(element_id: int | None = None, index: int = 1, output_format: str = 'json')
```

Returns text only.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `element_id` | `int \| None` | `None` | An element inside (or containing) the table; omit to pick by index |
| `index` | `int` | `1` | Which table on the page, 1-based, when element_id is omitted |
| `output_format` | `str` | `"json"` | "json" (rows keyed by header), "markdown", or "csv" |

Works on HTML `<table>` (honoring `<thead>`, an all-`<th>` first row, and `colspan`) and on ARIA `role="table"` and `role="grid"` widgets. Point at a table with any element inside it, or pick one by `index` (1-based). `output_format` is `json` (rows keyed by header), `markdown`, or `csv`.

```text
→ extract_table()
table #1: 2 row(s), 2 header(s)
[{"Name": "Apple", "Price": "1"}, {"Name": "Pear", "Price": "2"}]
```

## `extract_links` {#extract_links}

List the page's links as JSON: text, absolute href, and whether each is visible.

```python
extract_links(contains: str = '', limit: int = 100)
```

Returns text only.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `contains` | `str` | `""` | Only links whose text or URL contains this (case-insensitive) |
| `limit` | `int` | `100` | Maximum number of links to return (default 100) |

Every link, shadow DOM included, as `{text, href, visible}`, with absolute URLs and duplicates removed. `contains` filters by text or URL.

## `extract` {#extract}

Extract structured JSON from the page with a selector schema.

```python
extract(schema: dict[str, Any])
```

Returns text only.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `schema` | `dict[str, Any]` | required | The fields to extract, as described above |

Each value in the schema is a CSS selector, optionally with `@attr`:

| Value | Returns |
| --- | --- |
| `"h1"` | Text of the first match (a form field gives its value) |
| `"a@href"` | An attribute of the first match; `href` and `src` come back absolute |
| `"@href"` | An attribute of the scoped element itself |
| `[".tag"]` | Text of every match |
| `[{"_selector": ".card", …}]` | One object per match, fields relative to it |
| `{"_selector": "#main", …}` | One object scoped to the first match |

```text
→ extract({"title": "h1",
           "products": [{"_selector": ".product", "name": "h3",
                         "price": ".price", "url": "a@href"}]})
```

Selectors run against the main document, not inside iframes or shadow roots.

## See also

- [Extract data](/recipes/extract-data)
