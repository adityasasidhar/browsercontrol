"""Navigation policy: which URLs a tool may send the browser to.

Every tool that navigates to a caller-supplied URL calls ``check_navigation_allowed`` first.
It enforces two settings (read at call time, so tests can patch them):

* ``BROWSER_ALLOWED_DOMAINS``: when set, only these domains and their subdomains.
* ``BROWSER_ALLOW_UNSAFE_SCHEMES``: ``javascript:``, ``file:``, ``data:``, ``chrome:`` and
  friends are always blocked unless this is ``true``.

This guards the URLs the agent passes to navigation tools. It does not restrict links the
agent clicks, redirects a page performs, or JavaScript the agent runs.
"""

import ipaddress
import re
from urllib.parse import urlsplit

from browsercontrol.config import config

# Schemes that read local files, run script in the page, or open browser internals.
# ``view-source:`` wraps another URL (``view-source:file:///etc/passwd``), so it is blocked too.
UNSAFE_SCHEMES = frozenset(
    {
        "javascript",
        "file",
        "data",
        "chrome",
        "chrome-extension",
        "chrome-untrusted",
        "chrome-error",
        "devtools",
        "view-source",
        "blob",
        "filesystem",
    }
)

_HOST_CHARS = re.compile(r"[a-z0-9._-]+")
_CONTROL_EDGES = re.compile(r"^[\x00-\x20]+|[\x00-\x20]+$")
_MAX_SHOWN = 200


class NavigationBlockedError(ValueError):
    """Raised when the navigation policy refuses a URL. The message names the setting."""


def _shown(url: str) -> str:
    return url if len(url) <= _MAX_SHOWN else url[:_MAX_SHOWN] + "..."


def _normalize_host(raw: str | None) -> str | None:
    """Lowercase ASCII (IDNA) host without a trailing dot, or None if it is not a plain host."""
    if not raw:
        return None
    host = raw.strip().lower().rstrip(".")
    try:
        return str(ipaddress.ip_address(host))
    except ValueError:
        pass
    try:
        host = host.encode("idna").decode("ascii")
    except UnicodeError:
        return None
    # Anything else (percent escapes, slashes, spaces) is not a host a browser would agree on.
    return host if _HOST_CHARS.fullmatch(host) else None


def allowed_domains() -> list[str]:
    """The configured allowlist as bare lowercase hostnames (ports, paths, ``*.`` dropped)."""
    domains: list[str] = []
    for entry in config.allowed_domains:
        entry = entry.strip().removeprefix("*.").removeprefix(".")
        host = _normalize_host(urlsplit(entry if "//" in entry else "//" + entry).hostname)
        if host:
            domains.append(host)
    return domains


def _is_ip(host: str) -> bool:
    try:
        ipaddress.ip_address(host)
    except ValueError:
        return False
    return True


def _host_allowed(host: str, domains: list[str]) -> bool:
    # IP addresses match exactly: "1.2.3.4" has no subdomains.
    return any(host == d or (not _is_ip(d) and host.endswith("." + d)) for d in domains)


def check_navigation_allowed(url: str) -> None:
    """Raise ``NavigationBlockedError`` unless the configured policy lets the browser open ``url``."""
    # Browsers drop tabs and newlines, trim control characters and spaces at the ends, and
    # read "\" as "/" in web URLs, so judge the URL the way the browser will.
    cleaned = _CONTROL_EDGES.sub("", re.sub(r"[\t\r\n]", "", url))
    try:
        parts = urlsplit(cleaned.replace("\\", "/"))
    except ValueError:
        parts = urlsplit("")
    scheme = parts.scheme.lower()

    if not config.allow_unsafe_schemes and (
        scheme in UNSAFE_SCHEMES or (scheme == "about" and parts.path != "blank")
    ):
        raise NavigationBlockedError(
            f"Navigation to {_shown(url)!r} is blocked: {scheme}: URLs are not allowed. "
            "Set BROWSER_ALLOW_UNSAFE_SCHEMES=true to allow them."
        )

    if not config.allowed_domains or cleaned.lower() == "about:blank":
        return
    # A list with no usable entry (a typo) blocks everything rather than silently allowing all.
    domains = allowed_domains()
    host = _normalize_host(parts.hostname)
    if host is None or not _host_allowed(host, domains):
        raise NavigationBlockedError(
            f"Navigation to {_shown(url)!r} is blocked: "
            f"{'its host is not' if host else 'it has no recognizable host, so it is not'} "
            f"in BROWSER_ALLOWED_DOMAINS (allowed: {', '.join(domains) or 'none valid'}; "
            "subdomains of these are allowed)."
        )
