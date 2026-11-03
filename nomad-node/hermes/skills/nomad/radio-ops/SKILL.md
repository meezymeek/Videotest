---
name: radio-ops
description: Operate the Icom IC-705 and GMRS radios through rigctld, Direwolf, Pat (Winlink) and JS8Call — tune, change modes, beacon APRS, send Winlink email, and run digital-mode sessions, under the operator's license.
version: 0.1.0
platforms: [linux]
metadata:
  hermes:
    tags: [nomad, radio, ham, aprs, winlink]
    category: nomad
    requires_toolsets: [mcp_nomad]
---

# /radio-ops

Authorized to transmit: **only when the operator asks in this conversation**, and only on frequencies listed in `references/allowed-frequencies.md`. Always identify with the operator's callsign (from `~/.hermes/memories/USER.md`).

## Common tasks
- **Tune:** `radio.set_freq(<MHz>, <mode>)` where mode ∈ USB, LSB, FM, AM, CW, DATA-U. Confirm with `radio.get_state`.
- **APRS beacon/message:** `radio.send_aprs(text)`; text ≤ 67 chars. Position is appended automatically from `gps.fix`.
- **Winlink email:** `radio.winlink_send(to, subject, body)` queues; `radio.winlink_sync()` connects to the best RMS gateway from `references/gateways.md` (operator-maintained). Report connection result and any inbound mail.
- **Listen first:** before any TX, `sdr.monitor_start(freq, mode, 1)` and confirm the frequency is clear.
- **Voice on GMRS:** the GMRS radios have no CAT; you can only set PTT via `radio.ptt` on the GMRS sound-card interface and play TTS audio. Use for announcements only; never for anything requiring a license you don't have.

## Guardrails
- SWR > 3:1 → stop TX and tell the operator to check the antenna.
- Battery < 30% → max 5 W.
- Never run more than 10 minutes of continuous digital TX without a 1-minute pause (IC-705 thermal).
- Log every TX to `/incident-log` with time, freq, mode, power, purpose.

## References
- `references/allowed-frequencies.md` — operator-maintained allow-list (band, mode, max power).
- `references/gateways.md` — Winlink RMS gateways by band for the region.
