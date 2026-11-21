"""Show the agent's mouse input in the visible browser."""

import asyncio
import itertools
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager, suppress

from playwright.async_api import Error, Frame, Page

from browsercontrol.config import config

HIDE_POINTER_STYLE = "[data-bc-agent-pointer] { display: none !important; }"

_actions = itertools.count()

_TRACK_POINTER = """
([action, active]) => {
    const key = Symbol.for('browsercontrol.agentPointer');
    if (!active) {
        window[key]?.stop(action);
        return;
    }
    window[key] ??= (() => {
        const host = document.createElement('div');
        host.setAttribute('data-bc-agent-pointer', '');
        host.setAttribute('aria-hidden', 'true');
        host.style.cssText = 'all:initial;position:fixed!important;'
            + 'inset:0 auto auto 0!important;z-index:2147483647!important;'
            + 'pointer-events:none!important';
        const shadow = host.attachShadow({mode: 'closed'});
        const cursor = document.createElement('div');
        cursor.style.cssText = 'position:absolute;top:0;left:0;'
            + 'filter:drop-shadow(0 0 1px #111) drop-shadow(0 1px 2px #1118)';
        const arrow = document.createElement('div');
        arrow.style.cssText = 'width:20px;height:24px;background:#fff;'
            + 'clip-path:polygon(0 0, 100% 57%, 59% 62%, 79% 91%, 59% 100%, 39% 71%, 16% 94%)';
        const ring = document.createElement('div');
        ring.style.cssText = 'position:absolute;top:-12px;left:-12px;'
            + 'width:24px;height:24px;box-sizing:border-box;border:2px solid #7c6cff;'
            + 'border-radius:50%;opacity:0';
        cursor.append(ring, arrow);
        shadow.append(cursor);

        const actions = new Set();
        let listeners, idle, position, ripple;
        const hide = () => host.remove();
        const translate = (x, y) => 'translate(' + x + 'px,' + y + 'px)';
        const update = (event) => {
            if (!event.isTrusted || event.pointerType === 'touch') return;
            const {clientX: x, clientY: y} = event;
            const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
            if (!host.isConnected) {
                cursor.style.transition = 'none';
                cursor.style.transform = position ?? translate(x - 16, y - 16);
                document.documentElement.append(host);
                // Establish the starting position before applying the transition.
                cursor.getBoundingClientRect();
            }
            position = translate(x, y);
            cursor.style.transition = reduced ? 'none' : 'transform 140ms ease-out';
            cursor.style.transform = position;
            if (event.type === 'pointerdown') {
                ripple?.cancel();
                ripple = ring.animate(
                    [{opacity: 1, scale: reduced ? 1 : 0.6}, {opacity: 0, scale: 1}],
                    330,
                );
            }
            clearTimeout(idle);
            idle = setTimeout(hide, 1500);
        };

        return {
            start(action) {
                if (!actions.size) {
                    listeners = new AbortController();
                    const options = {capture: true, passive: true, signal: listeners.signal};
                    for (const type of ['pointermove', 'pointerdown', 'dragover', 'drop']) {
                        window.addEventListener(type, update, options);
                    }
                    window.addEventListener('pointerout', (event) => {
                        if (!event.relatedTarget || event.relatedTarget.tagName === 'IFRAME') {
                            hide();
                        }
                    }, options);
                }
                actions.add(action);
            },
            stop(action) {
                if (actions.delete(action) && !actions.size) listeners.abort();
            },
        };
    })();
    window[key].start(action);
}
"""


async def _set_tracking(frame: Frame, action: int, active: bool) -> None:
    # An unresponsive or navigating frame must not prevent the actual action.
    with suppress(Error, TimeoutError):
        async with asyncio.timeout(0.25):
            await frame.evaluate(_TRACK_POINTER, [action, active])


@asynccontextmanager
async def track_pointer(page: Page) -> AsyncIterator[None]:
    """Track trusted mouse events during an agent action, including in iframes."""
    if config.headless:
        yield
        return

    frames = page.frames
    action = next(_actions)
    try:
        await asyncio.gather(*(_set_tracking(frame, action, True) for frame in frames))
        yield
    finally:
        await asyncio.gather(*(_set_tracking(frame, action, False) for frame in frames))
