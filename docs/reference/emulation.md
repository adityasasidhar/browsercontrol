---
title: Emulation
description: Devices, dark mode, timezones, locations, and network throttling.
---

# Emulation

Settings apply to every tab in the session, including tabs opened later, and stay until `reset_emulation()`.

| Tool | Does | Returns |
| --- | --- | --- |
| [`list_devices`](#list_devices) | List device names accepted by emulate_device and create_session. | text |
| [`emulate_device`](#emulate_device) | Emulate a phone or tablet's screen size, user agent, and touch input. | text + screenshot |
| [`set_color_scheme`](#set_color_scheme) | Emulate prefers-color-scheme to check dark or light mode. | text + screenshot |
| [`set_timezone`](#set_timezone) | Make pages see a different timezone (Date, Intl). | text |
| [`set_geolocation`](#set_geolocation) | Report a fake location to sites, and grant them the geolocation permission. | text |
| [`throttle_network`](#throttle_network) | Slow the network down or take it offline, to test loading and offline states. | text |
| [`reset_emulation`](#reset_emulation) | Undo all emulation: device, geolocation, timezone, color scheme, and throttling. | text + screenshot |

## `list_devices` {#list_devices}

List device names accepted by emulate_device and create_session.

```python
list_devices(contains: str = '')
```

Returns text only.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `contains` | `str` | `""` | Only names containing this (case-insensitive), e.g. "iphone" |

Playwright's device catalog: about 140 phones, tablets, and desktops. `contains` filters by name.

## `emulate_device` {#emulate_device}

Emulate a phone or tablet's screen size, user agent, and touch input.

```python
emulate_device(name: str)
```

Returns text and a fresh annotated screenshot.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `name` | `str` | required | A device from list_devices(), e.g. "iPhone 13" or "Pixel 7" |

Sets the device's screen size, user agent, and touch input, then reloads. `"none"` returns to the desktop viewport. Pixel ratio and the mobile layout viewport need a new context: use `create_session(name, device=…)` for a fully faithful device.

## `set_color_scheme` {#set_color_scheme}

Emulate prefers-color-scheme to check dark or light mode.

```python
set_color_scheme(scheme: str = 'dark')
```

Returns text and a fresh annotated screenshot.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `scheme` | `str` | `"dark"` | "dark", "light", or "no-preference" |

Sets `prefers-color-scheme` to `dark`, `light`, or `no-preference`.

## `set_timezone` {#set_timezone}

Make pages see a different timezone (Date, Intl).

```python
set_timezone(timezone_id: str)
```

Returns text only.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `timezone_id` | `str` | required | IANA name such as "America/New_York" or "Asia/Tokyo"; "" resets |

IANA names such as `America/New_York` or `Asia/Tokyo`. `""` resets.

## `set_geolocation` {#set_geolocation}

Report a fake location to sites, and grant them the geolocation permission.

```python
set_geolocation(latitude: float, longitude: float, accuracy: float = 10.0)
```

Returns text only.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `latitude` | `float` | required | Latitude in degrees, e.g. 51.5074 |
| `longitude` | `float` | required | Longitude in degrees, e.g. -0.1278 |
| `accuracy` | `float` | `10.0` | Accuracy radius in meters (default 10) |

Reports a fake location to sites and grants them the geolocation permission.

## `throttle_network` {#throttle_network}

Slow the network down or take it offline, to test loading and offline states.

```python
throttle_network(profile: str = 'slow-3g')
```

Returns text only.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `profile` | `str` | `"slow-3g"` | "slow-3g", "fast-3g", "4g", "offline", or "none" to remove throttling |

`slow-3g`, `fast-3g`, `4g` (Chrome DevTools' presets), `offline`, or `none` to restore the network.

## `reset_emulation` {#reset_emulation}

Undo all emulation: device, geolocation, timezone, color scheme, and throttling.

```python
reset_emulation()
```

Returns text and a fresh annotated screenshot.

Undoes device, geolocation, timezone, color scheme, and throttling at once.

## See also

- [Mobile & dark mode](/recipes/responsive)
- [Test edge states](/recipes/edge-states)
