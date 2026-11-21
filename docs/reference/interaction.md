---
title: Interaction
description: Click, type, press keys, hover, drag, and batch several steps into one call with act.
---

# Interaction

Act on numbered elements. Every tool here returns a fresh annotated screenshot, so the next call has new numbers.

| Tool | Does | Returns |
| --- | --- | --- |
| [`click`](#click) | Click on an element by its ID number shown in the screenshot. | text + screenshot |
| [`type_text`](#type_text) | Type text into a text field by its ID number, replacing what it holds. | text + screenshot |
| [`press_key`](#press_key) | Press a keyboard key or key combination on the focused element. | text + screenshot |
| [`act`](#act) | Run several steps in one call and return one screenshot at the end. | text + screenshot |
| [`hover`](#hover) | Hover over an element by its ID number. | text + screenshot |
| [`double_click`](#double_click) | Double-click an element by its ID number (e.g. to open an item or select a word). | text + screenshot |
| [`right_click`](#right_click) | Right-click an element by its ID number to open its context menu. | text + screenshot |
| [`drag`](#drag) | Drag one element and drop it onto another (sortable lists, kanban cards, sliders). | text + screenshot |
| [`scroll_to_element`](#scroll_to_element) | Scroll to bring an element into view. | text + screenshot |
| [`click_at`](#click_at) | Click at specific x,y coordinates. | text + screenshot |
| [`wait`](#wait) | Wait for a specified time (useful for pages with animations or loading). | text + screenshot |

## `click` {#click}

Click on an element by its ID number shown in the screenshot.

```python
click(element_id: int)
```

Returns text and a fresh annotated screenshot.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `element_id` | `int` | required | The number label shown on the element in the screenshot |

Finds the numbered element itself, in its frame and through shadow DOM, scrolls it into view, and clicks it. It never clicks at stored coordinates, so an overlay can't steal the click silently.

- A **stale** ID (the element moved, vanished, or changed since the screenshot) is refused with a fresh screenshot. See [Stale IDs](/concepts/set-of-marks#stale-ids).
- A **disabled** element is refused immediately instead of waiting out the timeout.

```text
→ click(5)
Clicked element 5 (button: Sign in)
```

## `type_text` {#type_text}

Type text into a text field by its ID number, replacing what it holds.

```python
type_text(element_id: int, text: str)
```

Returns text and a fresh annotated screenshot.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `element_id` | `int` | required | The number label shown on the element |
| `text` | `str` | required | Text to type |

**Replaces** whatever the field holds. To append, read the current value with `get_text(id)` and type the combined text. Works on inputs, textareas, contenteditable regions, and `textbox`, `searchbox`, and `combobox` widgets. Checkboxes, buttons, dropdowns, and file inputs are refused with the right tool to use instead.

```text
→ type_text(3, "ada@example.com")
```

## `press_key` {#press_key}

Press a keyboard key or key combination on the focused element.

```python
press_key(key: str)
```

Returns text and a fresh annotated screenshot.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `key` | `str` | required | Key to press (e.g., "Enter", "Tab", "Escape", "ArrowDown", "Backspace"),  or a combination joined with "+" (e.g., "Control+A", "Shift+Tab",  "ControlOrMeta+C" for copy on any OS, "Control+Shift+T") |

Presses a key, or a combination joined with `+`, on whatever has focus.

```text
→ press_key("Enter")
→ press_key("Escape")             # close a modal
→ press_key("Control+A")
→ press_key("ControlOrMeta+C")    # copy on any OS
```

## `act` {#act}

Run several steps in one call and return one screenshot at the end.

```python
act(steps: list[dict[str, Any]], stop_on_error: bool = True)
```

Returns text and a fresh annotated screenshot.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `steps` | `list[dict[str, Any]]` | required | The steps to run in order (at most 25) |
| `stop_on_error` | `bool` | `True` | Stop at the first failing step (default True) |

Runs several steps and returns one screenshot. Every element ID refers to the screenshot taken **before** the call; a step whose element is gone (after a navigation, say) fails as stale, so put navigation last. At most 25 steps. `stop_on_error=False` keeps going after a failed step.

| `action` | Fields |
| --- | --- |
| `click`, `double_click`, `right_click`, `hover` | `element_id` |
| `type` | `element_id`, `text` |
| `select` | `element_id`, `option` |
| `check` | `element_id`, `checked` (default `true`) |
| `drag` | `element_id`, `target_id` |
| `press` | `key` |
| `scroll` | `direction`, `amount` |
| `navigate` | `url` |
| `wait` | `seconds` |
| `wait_for` | `text` or `selector`, `timeout_seconds` |

```text
→ act([{"action": "type", "element_id": 3, "text": "ada@example.com"},
       {"action": "type", "element_id": 4, "text": "hunter2"},
       {"action": "click", "element_id": 5}])
Ran 3 of 3 step(s), 0 failed:
  1. ok: typed 'ada@example.com' into [3]
  2. ok: typed ******* into [4]
  3. ok: clicked [5]
```

## `hover` {#hover}

Hover over an element by its ID number.

```python
hover(element_id: int)
```

Returns text and a fresh annotated screenshot.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `element_id` | `int` | required | The number label shown on the element |

Moves the pointer over the element, for tooltips, hover menus, and `:hover` styles. The returned screenshot shows what appeared.

## `double_click` {#double_click}

Double-click an element by its ID number (e.g. to open an item or select a word).

```python
double_click(element_id: int)
```

Returns text and a fresh annotated screenshot.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `element_id` | `int` | required | The number label shown on the element in the screenshot |

Double-clicks the element, for example to open an item or select a word.

## `right_click` {#right_click}

Right-click an element by its ID number to open its context menu.

```python
right_click(element_id: int)
```

Returns text and a fresh annotated screenshot.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `element_id` | `int` | required | The number label shown on the element in the screenshot |

Right-clicks the element to open its context menu.

## `drag` {#drag}

Drag one element and drop it onto another (sortable lists, kanban cards, sliders).

```python
drag(source_id: int, target_id: int)
```

Returns text and a fresh annotated screenshot.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `source_id` | `int` | required | The number label of the element to drag |
| `target_id` | `int` | required | The number label of the element to drop onto |

Drags one element onto another: sortable lists, kanban cards, sliders, and HTML5 drop zones. Both IDs come from the same, latest screenshot.

## `scroll_to_element` {#scroll_to_element}

Scroll to bring an element into view.

```python
scroll_to_element(element_id: int)
```

Returns text and a fresh annotated screenshot.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `element_id` | `int` | required | The number label shown on the element |

Scrolls until the element is in view. To reach something that has no number yet, use [`find`](/reference/navigation#find).

## `click_at` {#click_at}

Click at specific x,y coordinates.

```python
click_at(x: int, y: int)
```

Returns text and a fresh annotated screenshot.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `x` | `int` | required | X coordinate |
| `y` | `int` | required | Y coordinate |

Clicks at viewport coordinates. Use it only for a spot with no number, such as a canvas or a map; for anything numbered, `click` is safer.

## `wait` {#wait}

Wait for a specified time (useful for pages with animations or loading).

```python
wait(seconds: float = 1.0)
```

Returns text and a fresh annotated screenshot.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `seconds` | `float` | `1.0` | Time to wait in seconds (default: 1.0) |

Sleeps for a fixed time. Prefer [`wait_for`](/reference/waiting#wait_for), which waits for the thing you actually need.

## See also

- [Fill a form](/recipes/fill-a-form)
- [Forms](/reference/forms)
