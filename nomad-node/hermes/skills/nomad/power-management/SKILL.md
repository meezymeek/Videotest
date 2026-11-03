---
name: power-management
description: Read battery, solar and per-rail telemetry, switch device relays, and apply eco/normal/max power modes with forecasts of remaining runtime.
version: 0.1.0
platforms: [linux]
metadata:
  hermes:
    tags: [nomad, power, battery, solar, victron]
    category: nomad
    requires_toolsets: [mcp_nomad, mcp_homeassistant]
---

# /power-management

## Tools
- `power.status()` → `{soc_pct, volts, amps_net, watts_in_solar, watts_in_shore, watts_out, time_to_empty_h, rails: {compute, radio, rfbay, router, screen, fans}: watts, relays: {...}: on|off, mode}`.
- `power.relay(name, on)` — names: `ic705`, `sdr_hub`, `rnode`, `starlink`, `screen`, `fans_boost`, `aux1`, `aux2`.
- `power.mode("eco" | "normal" | "max")`.

## Modes
| Mode | Compute | Screen | SDR hub | IC-705 | Starlink | Notes |
|---|---|---|---|---|---|---|
| eco | LLM idle, no Whisper | off | off | RX only | off | Mesh, GPS, router stay on |
| normal | on demand | on | on | on | on if WAN needed | default |
| max | sustained | on | on | on | on | only on shore/solar surplus |

## Policy (from SOUL.md)
- SoC < 30% → `eco` + notify. SoC < 15% → shut non-essentials, notify on all channels. Never below 10% except for an active emergency message.
- Before any Whisper/large-model job, estimate the energy (Wh) from the rail wattage and say it.
- Shore power or solar surplus > 50 W over load → allow `max`.
- Nightly: at sunset compute expected overnight consumption vs SoC; if it won't make it to sunrise with 20% margin, go `eco` and say so.

## Forecasting
Use the last 24 h from HA history (`sensor.nomad_solar_watts`, `sensor.nomad_load_watts`) to project. State assumptions.
