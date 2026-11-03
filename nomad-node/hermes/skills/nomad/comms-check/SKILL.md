---
name: comms-check
description: Run the full NOMAD communications self-test across every link (power, net, GPS, mesh, APRS/SDR loopback, satellite, cellular) and return a pass/fail table.
version: 0.1.0
platforms: [linux]
metadata:
  hermes:
    tags: [nomad, radio, comms, diagnostics]
    category: nomad
    requires_toolsets: [mcp_nomad, mcp_homeassistant]
---

# /comms-check

Authorized to transmit: **yes**, but only the test transmissions listed here (one APRS packet, one Meshtastic ping, one RockBLOCK test if `--sat` is passed).

## Procedure
1. `power.status` — fail if SoC < 15% (abort everything else; report).
2. `env.status` — warn if case temp > 45 °C.
3. `gps.fix` — pass if 3D fix with < 10 m HDOP in the last 60 s.
4. `net.status` — list each WAN (starlink, cellular) and LAN health (router, switch reachable; Wi-Fi SSIDs up).
5. **Mesh:** `mesh.send("NOMAD comms-check <time>", to=<roaming node>)`; pass if ack within 30 s.
6. **APRS loopback:** `sdr.monitor_start(144.39, "fm", 1)` in the background, then `radio.send_aprs("NOMAD comms-check")`; pass if the SDR decode shows our callsign.
7. **Rig:** `radio.get_state` — pass if rigctld answers and SWR last-reading < 2:1 (if available).
8. **Cellular SMS:** send "comms-check" to the operator's phone number from HA `notify.sms`; pass if HA logs delivery.
9. **Satellite (only with `--sat`):** `sat.send("NOMAD comms-check")`; pass if the modem reports MO queue sent.
10. **Winlink (only with `--winlink`):** `radio.winlink_sync`; pass if a connection completed in the log.

## Output
A table: `Link | Result | Detail | Next step`. Then one line: overall GREEN / YELLOW / RED. Write the result to the incident log via `/incident-log`.

## Rules
- Never retry a transmission more than once.
- If `power.status` fails, do not key anything.
- Keep the report under 25 lines on Matrix; on Meshtastic send only the one-line summary.
