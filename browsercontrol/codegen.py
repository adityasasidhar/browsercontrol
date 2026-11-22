"""Turn a session's action log into a replayable Playwright test.

Element IDs only mean something against one screenshot, so every logged action
records the element by stable locators instead: test id, ARIA role and name,
label, placeholder, text, or a CSS path. Each candidate is checked against the
live page before the action runs and the first one that matches exactly that
element is kept.
"""

import json
import re
from typing import Any

from playwright.async_api import ElementHandle, Frame, Locator

# Runs on the element. Returns candidate locators, best first.
DESCRIBE_JS = r"""
el => {
    const clean = s => (s || '').replace(/\s+/g, ' ').trim();
    const tag = el.tagName.toLowerCase();
    const type = (el.getAttribute('type') || '').toLowerCase();
    const implicitRole = () => {
        if (tag === 'a' && el.hasAttribute('href')) return 'link';
        if (tag === 'button') return 'button';
        if (tag === 'select') return el.multiple || el.size > 1 ? 'listbox' : 'combobox';
        if (tag === 'textarea') return 'textbox';
        if (/^h[1-6]$/.test(tag)) return 'heading';
        if (tag !== 'input') return '';
        if (['button', 'submit', 'reset', 'image'].includes(type)) return 'button';
        if (['checkbox', 'radio'].includes(type)) return type;
        if (type === 'search') return 'searchbox';
        if (type === 'number') return 'spinbutton';
        if (['', 'text', 'email', 'tel', 'url'].includes(type)) {
            return el.hasAttribute('list') ? 'combobox' : 'textbox';
        }
        return '';
    };
    const role = (el.getAttribute('role') || '').split(' ')[0] || implicitRole();
    let label = el.getAttribute('aria-label') || '';
    const labelledBy = el.getAttribute('aria-labelledby');
    if (!label && labelledBy) {
        label = labelledBy.split(/\s+/)
            .map(id => (el.ownerDocument.getElementById(id) || {}).textContent || '').join(' ');
    }
    if (!label && el.labels && el.labels.length) {
        label = Array.from(el.labels).map(l => l.textContent).join(' ');
    }
    label = clean(label);
    const text = clean(el.innerText || '');
    const nameFromText = ['button', 'link', 'checkbox', 'radio', 'tab', 'menuitem', 'option',
                          'heading', 'switch'].includes(role);
    let name = label || (nameFromText ? text : '');
    if (!name && tag === 'input' && ['button', 'submit', 'reset'].includes(type)) {
        name = clean(el.value);
    }
    if (!name) name = clean(el.getAttribute('title'));
    if (!name && ['textbox', 'searchbox', 'combobox'].includes(role)) {
        name = clean(el.getAttribute('placeholder'));
    }

    const out = [];
    const testId = el.getAttribute('data-testid');
    if (testId) out.push({kind: 'testid', value: testId});
    if (role && name && name.length <= 80) out.push({kind: 'role', role, name});
    const isField = ['input', 'textarea', 'select'].includes(tag);
    if (label && isField && label.length <= 80) out.push({kind: 'label', value: label});
    const placeholder = el.getAttribute('placeholder');
    if (placeholder) out.push({kind: 'placeholder', value: placeholder});
    if (text && !isField && text.length <= 60) out.push({kind: 'text', value: text});
    if (el.id && /^[A-Za-z][\w-]*$/.test(el.id)) out.push({kind: 'css', value: '#' + el.id});
    const nameAttr = el.getAttribute('name');
    if (nameAttr && /^[\w.\-\[\]]+$/.test(nameAttr)) {
        out.push({kind: 'css', value: `${tag}[name="${nameAttr}"]`});
    }

    // Structural fallback: nth-of-type steps up to an id, crossing open shadow
    // roots with a descendant combinator (Playwright's CSS pierces them).
    const steps = [];
    let node = el;
    while (node && node.nodeType === 1) {
        const t = node.tagName.toLowerCase();
        if (node !== el && node.id && /^[A-Za-z][\w-]*$/.test(node.id)) {
            steps.unshift('#' + node.id);
            break;
        }
        const parent = node.parentNode;
        let step = t;
        if (parent && parent.children) {
            const same = Array.from(parent.children).filter(c => c.tagName === node.tagName);
            if (same.length > 1) step += `:nth-of-type(${same.indexOf(node) + 1})`;
        }
        steps.unshift(step);
        if (parent instanceof ShadowRoot) {
            steps.unshift('\u00a7');
            node = parent.host;
        } else {
            node = parent;
        }
        if (t === 'body') break;
    }
    const css = steps.join(' > ').split(' > \u00a7 > ').join(' ');
    out.push({kind: 'css', value: css});
    return {candidates: out, password: type === 'password', tag};
}
"""


def _build(frame: Frame, candidate: dict[str, Any]) -> Locator:
    kind = candidate["kind"]
    if kind == "testid":
        return frame.get_by_test_id(candidate["value"])
    if kind == "role":
        return frame.get_by_role(candidate["role"], name=candidate["name"], exact=True)
    if kind == "label":
        return frame.get_by_label(candidate["value"], exact=True)
    if kind == "placeholder":
        return frame.get_by_placeholder(candidate["value"], exact=True)
    if kind == "text":
        return frame.get_by_text(candidate["value"], exact=True)
    return frame.locator(candidate["value"])


async def _pick(frame: Frame, handle: ElementHandle, info: dict[str, Any]) -> dict[str, Any]:
    """The first candidate that resolves to exactly this element (CSS path as a last resort)."""
    for candidate in info["candidates"]:
        try:
            located = _build(frame, candidate)
            if await located.count() != 1:
                continue
            if await located.evaluate("(el, target) => el === target", handle):
                return dict(candidate)
        except Exception:  # nosec B112 - a candidate that fails to build is skipped
            continue
    return {**info["candidates"][-1], "first": True}


async def describe_target(locator: Locator) -> dict[str, Any]:
    """Describe an element so a generated test can find it again without SoM IDs."""
    handle = await locator.element_handle(timeout=2000)
    if handle is None:
        raise ValueError("element is gone")
    frame = await handle.owner_frame()
    if frame is None:
        raise ValueError("element has no frame")
    info = await handle.evaluate(DESCRIBE_JS)
    target = await _pick(frame, handle, info)
    target["password"] = bool(info.get("password"))

    # Each enclosing <iframe>, outermost first, described the same way.
    frames: list[dict[str, Any]] = []
    current = frame
    while current.parent_frame is not None:
        owner = await current.frame_element()
        frames.insert(
            0, await _pick(current.parent_frame, owner, await owner.evaluate(DESCRIBE_JS))
        )
        current = current.parent_frame
    target["frames"] = frames
    return target


# ----- rendering ---------------------------------------------------------------

_q = json.dumps


def _locator_py(target: dict[str, Any]) -> str:
    base = "page"
    for frame in target.get("frames", []):
        base += f".frame_locator({_q(_css_or_any(frame))})"
    kind = target["kind"]
    if kind == "testid":
        expr = f"{base}.get_by_test_id({_q(target['value'])})"
    elif kind == "role":
        expr = f"{base}.get_by_role({_q(target['role'])}, name={_q(target['name'])}, exact=True)"
    elif kind == "label":
        expr = f"{base}.get_by_label({_q(target['value'])}, exact=True)"
    elif kind == "placeholder":
        expr = f"{base}.get_by_placeholder({_q(target['value'])}, exact=True)"
    elif kind == "text":
        expr = f"{base}.get_by_text({_q(target['value'])}, exact=True)"
    else:
        expr = f"{base}.locator({_q(target['value'])})"
    return expr + (".first" if target.get("first") else "")


def _locator_ts(target: dict[str, Any]) -> str:
    base = "page"
    for frame in target.get("frames", []):
        base += f".frameLocator({_q(_css_or_any(frame))})"
    kind = target["kind"]
    if kind == "testid":
        expr = f"{base}.getByTestId({_q(target['value'])})"
    elif kind == "role":
        expr = (
            f"{base}.getByRole({_q(target['role'])}, {{ name: {_q(target['name'])}, exact: true }})"
        )
    elif kind == "label":
        expr = f"{base}.getByLabel({_q(target['value'])}, {{ exact: true }})"
    elif kind == "placeholder":
        expr = f"{base}.getByPlaceholder({_q(target['value'])}, {{ exact: true }})"
    elif kind == "text":
        expr = f"{base}.getByText({_q(target['value'])}, {{ exact: true }})"
    else:
        expr = f"{base}.locator({_q(target['value'])})"
    return expr + (".first()" if target.get("first") else "")


def _css_or_any(frame_target: dict[str, Any]) -> str:
    """frame_locator() takes a selector; role/text candidates become internal selectors."""
    kind = frame_target["kind"]
    if kind == "css":
        return str(frame_target["value"])
    if kind == "testid":
        return f'[data-testid="{frame_target["value"]}"]'
    if kind == "role":
        return f'internal:role={frame_target["role"]}[name="{frame_target["name"]}"s]'
    return "iframe"


def _route_pattern(pattern: str, lang: str) -> str:
    if pattern.startswith("re:"):
        regex = pattern[3:]
        return f"re.compile({_q(regex)})" if lang == "py" else f"new RegExp({_q(regex)})"
    if "*" in pattern or "?" in pattern:
        return _q(pattern)
    return _q(f"**/*{pattern}*")


def _assert_url(pattern: str, py: bool) -> str:
    """expect(page).to_have_url() for a url_matches pattern: regex, glob, or substring."""
    if pattern.startswith("re:"):
        arg = f"re.compile({_q(pattern[3:])})" if py else f"new RegExp({_q(pattern[3:])})"
    elif "*" in pattern or "?" in pattern:
        arg = _q(pattern)
    else:
        arg = (
            f"re.compile(re.escape({_q(pattern)}))"
            if py
            else f"new RegExp({_q(re.escape(pattern))})"
        )
    return f"expect(page).to_have_url({arg})" if py else f"await expect(page).toHaveURL({arg});"


def _step(action: dict[str, Any], lang: str, secrets: list[str]) -> list[str]:
    """Lines for one logged action in Python ("py") or TypeScript ("ts")."""
    py = lang == "py"
    kind = action["action"]
    target = action.get("target")
    loc = (_locator_py(target) if py else _locator_ts(target)) if target else None
    end = "" if py else ";"
    aw = "" if py else "await "

    if kind == "navigate":
        return [f"{aw}page.goto({_q(action['url'])}){end}"]
    if kind in ("back", "forward", "reload"):
        name = {
            "back": "go_back" if py else "goBack",
            "forward": "go_forward" if py else "goForward",
        }
        return [f"{aw}page.{name.get(kind, 'reload')}(){end}"]
    if kind == "press":
        return [f"{aw}page.keyboard.press({_q(action['key'])}){end}"] * int(action.get("count", 1))
    if kind == "scroll":
        return [f"{aw}page.mouse.wheel({action.get('dx', 0)}, {action.get('dy', 0)}){end}"]
    if kind == "wait":
        fn = "wait_for_timeout" if py else "waitForTimeout"
        return [f"{aw}page.{fn}({int(action['ms'])}){end}"]
    if kind == "wait_for_text":
        text = _q(action["text"])
        if py:
            return [f"expect(page.get_by_text({text}).first).to_be_visible()"]
        return [f"await expect(page.getByText({text}).first()).toBeVisible();"]
    if kind == "dialog":
        prompt = action.get("prompt_text")
        if action.get("accept"):
            answer = f"accept({_q(prompt)})" if prompt is not None else "accept()"
        else:
            answer = "dismiss()"
        if py:
            return [f'page.once("dialog", lambda dialog: dialog.{answer})']
        return [f'page.once("dialog", (dialog) => dialog.{answer});']
    if kind == "mock":
        pattern = _route_pattern(action["pattern"], lang)
        if action.get("abort"):
            return [
                f"{aw}page.route({pattern}, {'lambda route: route.abort()' if py else '(route) => route.abort()'}){end}"
            ]
        status, body, ctype = (
            action.get("status", 200),
            _q(action.get("body", "")),
            _q(action.get("content_type", "text/plain")),
        )
        if py:
            return [
                f"page.route({pattern}, lambda route: route.fulfill(status={status}, body={body}, content_type={ctype}))"
            ]
        return [
            f"await page.route({pattern}, (route) => route.fulfill({{ status: {status}, body: {body}, contentType: {ctype} }}));"
        ]

    if kind == "assert_url":
        return [_assert_url(action["pattern"], py)]
    if kind == "assert_text" and loc is None:
        text = _q(action["text"])
        if action.get("present", True):
            if py:
                return [f"expect(page.get_by_text({text}).first).to_be_visible()"]
            return [f"await expect(page.getByText({text}).first()).toBeVisible();"]
        if py:
            return [f"expect(page.get_by_text({text})).to_have_count(0)"]
        return [f"await expect(page.getByText({text})).toHaveCount(0);"]

    if loc is None:
        return [f"{'#' if py else '//'} {kind}: not replayable (element could not be described)"]
    if kind == "click":
        count, button = int(action.get("click_count", 1)), action.get("button", "left")
        if count == 2:
            return [f"{aw}{loc}.{'dblclick'}(){end}"]
        if button != "left":
            arg = f"button={_q(button)}" if py else f"{{ button: {_q(button)} }}"
            return [f"{aw}{loc}.click({arg}){end}"]
        return [f"{aw}{loc}.click(){end}"]
    if kind == "fill":
        if target and target.get("password"):
            var = f"BC_SECRET_{len(secrets) + 1}"
            secrets.append(var)
            value = f'os.environ["{var}"]' if py else f"process.env.{var}!"
        else:
            value = _q(action.get("text", ""))
        return [f"{aw}{loc}.fill({value}){end}"]
    if kind == "assert_text":
        text = _q(action["text"])
        present = action.get("present", True)
        if py:
            fn = "to_contain_text" if present else "not_to_contain_text"
            return [f"expect({loc}).{fn}({text})"]
        return [f"await expect({loc}).{'' if present else 'not.'}toContainText({text});"]
    if kind == "assert_value":
        if "text" not in action:
            return [f"{'#' if py else '//'} assert_value: password field value not recorded"]
        fn = "to_have_value" if py else "toHaveValue"
        return [f"{aw}expect({loc}).{fn}({_q(action['text'])}){end}"]
    if kind == "hover":
        return [f"{aw}{loc}.hover(){end}"]
    if kind == "select":
        fn = "select_option" if py else "selectOption"
        return [f"{aw}{loc}.{fn}({_q(action['option'])}){end}"]
    if kind == "check":
        fn = "set_checked" if py else "setChecked"
        flag = (
            ("True" if py else "true")
            if action.get("checked", True)
            else ("False" if py else "false")
        )
        return [f"{aw}{loc}.{fn}({flag}){end}"]
    if kind == "upload":
        fn = "set_input_files" if py else "setInputFiles"
        return [f"{aw}{loc}.{fn}({_q(action['path'])}){end}"]
    if kind == "drag":
        dest = action.get("dest")
        if not dest:
            return [f"{'#' if py else '//'} drag: drop target could not be described"]
        dest_loc = _locator_py(dest) if py else _locator_ts(dest)
        fn = "drag_to" if py else "dragTo"
        return [f"{aw}{loc}.{fn}({dest_loc}){end}"]
    return [f"{'#' if py else '//'} {kind}: not supported by the generator"]


def _test_name(name: str) -> str:
    slug = re.sub(r"\W+", "_", name.strip().lower()).strip("_")
    return slug or "recorded_session"


def render_test(actions: list[dict[str, Any]], name: str, language: str = "python") -> str:
    """Render logged actions as a pytest-playwright (python) or @playwright/test (typescript) test."""
    slug = _test_name(name)
    secrets: list[str] = []
    if language == "typescript":
        body = [line for action in actions for line in _step(action, "ts", secrets)]
        header = ["import { test, expect } from '@playwright/test';", ""]
        if secrets:
            header.append(f"// Set these environment variables first: {', '.join(secrets)}")
        lines = [*header, f"test({_q(slug)}, async ({{ page }}) => {{"]
        lines += [f"  {line}" for line in body] or ["  // no actions were recorded"]
        lines.append("});")
        return "\n".join(lines) + "\n"
    if language != "python":
        raise ValueError(f"Unsupported language {language!r}: use 'python' or 'typescript'")

    body = [line for action in actions for line in _step(action, "py", secrets)]
    lines = ['"""Generated by BrowserControl from a recorded agent session."""', ""]
    stdlib = [
        m for m, used in (("os", secrets), ("re", any("re.compile" in b for b in body))) if used
    ]
    lines += [f"import {m}" for m in stdlib] + ([""] if stdlib else [])
    lines += ["from playwright.sync_api import Page, expect", "", ""]
    if secrets:
        lines.append(f"# Set these environment variables first: {', '.join(secrets)}")
    lines.append(f"def test_{slug}(page: Page) -> None:")
    lines += [f"    {line}" for line in body] or ["    pass  # no actions were recorded"]
    return "\n".join(lines) + "\n"
