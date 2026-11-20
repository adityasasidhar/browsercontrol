# Interaction

Click, type, hover, press keys, and wait — the core "do something on the page" tools. Every tool here returns an **annotated screenshot + element map** so the next call has fresh IDs.

!!! info "Element IDs"
    Use the `[id]` you see in the most recent screenshot or element map. IDs reset after every action.

---

## `click`

Click an interactive element by its **Set of Marks** number.

```python
click(element_id: int) -> tuple[str, Image]
```

**Parameters**

| Name | Type | Description |
|---|---|---|
| `element_id` | `int` | The number label shown on the element in the latest screenshot. |

**Behavior**

- Finds the numbered element itself (by its `data-bc-id` tag, in the right frame and through shadow DOM), not whatever sits at its old coordinates.
- Refuses stale IDs: if the element was removed or moved since the screenshot, returns `Element N is stale (...)` with a fresh screenshot instead of clicking.
- Scrolls the element into view first.
- Returns a fresh annotated screenshot.

**Example**

```text
→ click(5)             # clicks the 5th element from the latest element map
```

**Error handling**

If the element ID isn't in the current map, returns:

```text
Error: Element 5 not found. Valid IDs: [1, 2, 3, 4, 6, 7, ...]
```

…plus a fresh screenshot so the agent can pick a valid ID.

---

## `click_at`

Click at raw pixel coordinates.

```python
click_at(x: int, y: int) -> tuple[str, Image]
```

**Parameters**

| Name | Type | Description |
|---|---|---|
| `x` | `int` | X coordinate in viewport pixels. |
| `y` | `int` | Y coordinate in viewport pixels. |

**When to use**

Use `click_at` when you have pixel coordinates from a vision-language model rather than an element ID. For SoM-driven clicks, prefer `click`.

---

## `type_text`

Type text into an input element by its **Set of Marks** number.

```python
type_text(element_id: int, text: str) -> tuple[str, Image]
```

**Parameters**

| Name | Type | Description |
|---|---|---|
| `element_id` | `int` | The number label shown on the element. |
| `text` | `str` | The text to type. |

**Behavior**

- Uses Playwright's `element.fill()` — atomic, not char-by-char typing.
- Works with `<input>`, `<textarea>`, and `contenteditable` elements.
- The element is scrolled into view first.
- A fresh annotated screenshot is returned.

**Examples**

```text
→ type_text(2, "alice@example.com")       # email field
→ type_text(3, "hunter2")                 # password field
→ type_text(4, "Hello, world!")           # textarea
```

---

## `press_key`

Key combinations work too: `Control+A`, `Shift+Tab`, `ControlOrMeta+C` (copy on any OS).


Press a single keyboard key.

```python
press_key(key: str) -> tuple[str, Image]
```

**Parameters**

| Name | Type | Description |
|---|---|---|
| `key` | `str` | The key name. Common: `Enter`, `Tab`, `Escape`, `Backspace`, `Delete`, `ArrowUp`, `ArrowDown`, `ArrowLeft`, `ArrowRight`, `Home`, `End`, `PageUp`, `PageDown`. Single characters also work. |

**Examples**

```text
→ press_key("Enter")                       # submit a form
→ press_key("Escape")                      # close a modal
→ press_key("ArrowDown")                   # navigate a menu
→ press_key("Backspace")                   # delete a character
```

---

## `hover`

Hover over an element by its **Set of Marks** number. Useful for triggering tooltips, dropdowns, and CSS hover effects.

```python
hover(element_id: int) -> tuple[str, Image]
```

---

## `scroll_to_element`

Scroll the page until an element is visible in the viewport.

```python
scroll_to_element(element_id: int) -> tuple[str, Image]
```

**Parameters**

| Name | Type | Description |
|---|---|---|
| `element_id` | `int` | The number label of the element to bring into view. |

---

## `wait`

Sleep for a number of seconds. Useful for animations, lazy-loaded content, or transitions.

```python
wait(seconds: float = 1.0) -> tuple[str, Image]
```

**Parameters**

| Name | Type | Default | Description |
|---|---|---|---|
| `seconds` | `float` | `1.0` | How long to sleep before returning. |

**Examples**

```text
→ wait(0.5)                                # short pause for an animation
→ wait(3.0)                                # wait for a slow fetch
```

---

## `double_click`

```python
double_click(element_id: int) -> tuple[str, Image]
```

## `right_click`

Opens the element's context menu.

```python
right_click(element_id: int) -> tuple[str, Image]
```

## `drag`

Drag one element onto another (sortable lists, kanban boards, file drop zones
built on HTML5 drag-and-drop).

```python
drag(source_id: int, target_id: int) -> tuple[str, Image]
```

---

## `act`

Run several steps in one call and get one screenshot back, saving round-trips
on forms and multi-step flows.

```python
act(steps: list[dict], stop_on_error: bool = True) -> tuple[str, Image]
```

Each step is an object with `action` plus its fields:

| `action` | Fields |
|---|---|
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

All element IDs refer to the screenshot taken **before** the call. A step whose
element has gone (after a navigation, say) fails as stale, so put navigation last.
At most 25 steps.

```text
→ act([{"action": "type", "element_id": 3, "text": "ada@example.com"},
       {"action": "type", "element_id": 4, "text": "hunter2"},
       {"action": "click", "element_id": 5}])
Ran 3 of 3 step(s), 0 failed:
  1. ok: typed 'ada@example.com' into [3]
  2. ok: typed ******* into [4]
  3. ok: clicked [5]
```

---

## See also

- **[Navigation tools](navigation.md)** — open URLs, scroll
- **[Forms tools](forms.md)** — select, check, upload
- **[Fill a form guide](../guides/fill-forms.md)** — typed example
