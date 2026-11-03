---
name: net-ops
description: Inspect and manage the OpenWrt router and MikroTik switch — WAN failover, clients, VLAN placement, Wi-Fi SSIDs, DNS names, and the Ollama/OpenAI inference endpoint advertised to LAN devices.
version: 0.1.0
platforms: [linux]
metadata:
  hermes:
    tags: [nomad, network, openwrt, mikrotik, wan]
    category: nomad
    requires_toolsets: [mcp_nomad]
---

# /net-ops

## Tools
- `net.status()` → WANs (starlink/cellular: up, latency, data used), Wi-Fi radios, VLAN health, switch port states, inference endpoint health (`/v1/models` on :8080, Ollama `:11434`).
- `net.clients()` → MAC, IP, hostname, VLAN, signal, traffic.
- `net.wan_failover(prefer)` → "starlink" | "cellular" | "auto".
- `net.vlan_isolate(mac)` → moves a client to `guest` and blocks LAN.
- `net.dns_add(name, ip)` → adds `name.nomad.lan`.
- `net.wifi(ssid, enabled)` → toggle an SSID (e.g. turn off `nomad-guest`).

## VLAN rules (DESIGN.md §3.3)
10 mgmt (router, switch, compute mgmt), 20 lan (users), 30 iot (ESP32, relays), 40 rf, 50 guest, 60 pentest. The agent only reaches the router via mgmt. Never move the compute node or router off mgmt. Never open pentest → anything.

## Behaviors
- On WAN change, post one line to Matrix: `WAN: <old> → <new> (<reason>)`.
- Cellular data is metered: when on cellular, disable Syncthing/Jellyfin/Nextcloud WAN sync via HA switches and say so.
- "Who's on the network?" → `net.clients()` grouped by VLAN; flag unknown MACs.
- "Point my phone at the AI" → reply with `http://ai.nomad.lan:11434` (Ollama) and `http://ai.nomad.lan:8080/v1` (OpenAI-compatible) and the SSID.
