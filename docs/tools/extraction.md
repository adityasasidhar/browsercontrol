# Extraction

Pull structured data out of the page as JSON instead of reading it off a screenshot.
These tools return text only (no screenshot).

---

## `extract_table`

```python
extract_table(element_id: int | None = None, index: int = 1, output_format: str = "json") -> str
```

| Name | Type | Default | Description |
|---|---|---|---|
| `element_id` | `int \| None` | `None` | Any element inside (or containing) the table. |
| `index` | `int` | `1` | Which table on the page, 1-based, when `element_id` is omitted. |
| `output_format` | `str` | `"json"` | `json` (rows keyed by header), `markdown`, or `csv`. |

Works on HTML `<table>` (honouring `<thead>`, a leading all-`<th>` row, and
`colspan`) and on ARIA `role="table"`/`role="grid"` widgets. Nested tables are
not counted separately.

```text
→ extract_table()
table #1: 2 row(s), 2 header(s)
[{"Name": "Apple", "Price": "1"}, {"Name": "Pear", "Price": "2"}]
```

---

## `extract_links`

```python
extract_links(contains: str = "", limit: int = 100) -> str
```

Every link on the page (shadow DOM included) as `{text, href, visible}`, with
absolute URLs, de-duplicated. `contains` filters by text or URL.

---

## `extract`

Schema-driven extraction with CSS selectors.

```python
extract(schema: dict) -> str
```

| Schema value | Meaning |
|---|---|
| `"h1"` | Text of the first match (a form field gives its value). |
| `"a@href"` | An attribute of the first match. `href` and `src` come back absolute. |
| `"@href"` | An attribute of the scoped element itself. |
| `[".tag"]` | Text of **every** match. |
| `[{"_selector": ".card", ...}]` | One object per match, fields relative to it. |
| `{"_selector": "#main", ...}` | One object scoped to the first match. |

```text
→ extract({"title": "h1",
           "products": [{"_selector": ".product", "name": "h3",
                         "price": ".price", "url": "a@href"}]})
{
  "title": "Shop",
  "products": [
    {"name": "Widget", "price": "$5", "url": "https://shop.test/w"},
    {"name": "Gadget", "price": "$7", "url": "https://shop.test/g"}
  ]
}
```

Selectors run against the main document, not iframes or shadow roots.
