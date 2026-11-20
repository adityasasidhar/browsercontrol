# Emulation

Test how a site behaves on other devices, places, and networks. Settings apply to
every open tab in your session and to tabs opened later. `reset_emulation()`
undoes all of them.

---

## `list_devices`

```python
list_devices(contains: str = "") -> str
```

Playwright's device catalogue (about 140 phones, tablets, and desktops).

## `emulate_device`

```python
emulate_device(name: str) -> tuple[str, Image]
```

Sets the device's screen size, user agent, and touch input, then reloads.
`"none"` returns to the desktop viewport.

!!! note "Pixel ratio and mobile layout"
    Device pixel ratio and the mobile layout viewport can only be set when a
    browser context is created. For a fully faithful device use
    [`create_session(name, device="iPhone 13")`](sessions.md#create_session).

## `set_geolocation`

```python
set_geolocation(latitude: float, longitude: float, accuracy: float = 10.0) -> str
```

Also grants sites the geolocation permission.

## `set_timezone`

```python
set_timezone(timezone_id: str) -> str
```

IANA names such as `America/New_York`; `""` resets.

## `set_color_scheme`

```python
set_color_scheme(scheme: str = "dark") -> tuple[str, Image]
```

`dark`, `light`, or `no-preference` for `prefers-color-scheme`.

## `throttle_network`

```python
throttle_network(profile: str = "slow-3g") -> str
```

`slow-3g`, `fast-3g`, `4g` (Chrome DevTools' presets), `offline`, or `none`.

## `reset_emulation`

```python
reset_emulation() -> tuple[str, Image]
```

See also the **[mobile responsive guide](../guides/mobile-responsive.md)**.
