---
title: Tabs
description: Open, list, switch between, and close tabs.
---

# Tabs

Tabs belong to the current [session](/concepts/sessions) and share its cookies. Each keeps its own element map. Indexes start at 0.

| Tool | Does | Returns |
| --- | --- | --- |
| [`create_tab`](#create_tab) | Create a new tab and switch to it. | text + screenshot |
| [`list_tabs`](#list_tabs) | List all open tabs with their indices, titles, and URLs. | text |
| [`switch_tab`](#switch_tab) | Switch to a specific tab by its index. | text + screenshot |
| [`close_tab`](#close_tab) | Close a specific tab by its index. | text + screenshot |

## `create_tab` {#create_tab}

Create a new tab and switch to it.

```python
create_tab(url: str | None = None)
```

Returns text and a fresh annotated screenshot.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `url` | `str \| None` | `None` | Optional URL to open in the new tab. |

Opens a tab, switches to it, and returns its screenshot. Without `url`, the tab is blank.

## `list_tabs` {#list_tabs}

List all open tabs with their indices, titles, and URLs.

```python
list_tabs()
```

Returns text only.

Text only, so it's cheap. `*` marks the active tab.

```text
Open Tabs:
  [0] GitHub - https://github.com
* [1] Hacker News - https://news.ycombinator.com
```

## `switch_tab` {#switch_tab}

Switch to a specific tab by its index.

```python
switch_tab(index: int)
```

Returns text and a fresh annotated screenshot.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `index` | `int` | required | The 0-based index of the tab to switch to. |

Focuses the tab and returns its screenshot and element map.

## `close_tab` {#close_tab}

Close a specific tab by its index.

```python
close_tab(index: int)
```

Returns text and a fresh annotated screenshot.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `index` | `int` | required | The 0-based index of the tab to close. |

Closes the tab. Closing the active tab switches to another open one. Indexes after it shift down by one.

## See also

- [Work across tabs](/recipes/tabs)
