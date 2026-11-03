---
name: mesh-ops
description: Send and read Meshtastic and Reticulum/LXMF messages, list mesh nodes with signal and position, and relay messages between the mesh and other channels.
version: 0.1.0
platforms: [linux]
metadata:
  hermes:
    tags: [nomad, lora, meshtastic, reticulum]
    category: nomad
    requires_toolsets: [mcp_nomad]
---

# /mesh-ops

Authorized to transmit: **yes** (LoRa ISM, license-free). Keep traffic light — the mesh is shared and slow.

## Tools
- `mesh.nodes()` — node id, short name, last heard, SNR/RSSI, battery, position.
- `mesh.send(text, to=None, channel=0)` — DM (`to=<node id>`) or channel broadcast. ≤ 200 chars. Returns ack status.
- `mesh.recent(n)` — last n received messages.
- `rns.send(dest_hash, text)` — Reticulum LXMF message (encrypted, can be long; delivery may be delayed until a path exists).

## Behaviors
- When asked "who's around", answer from `mesh.nodes()` with distance/bearing from `gps.fix` if positions exist.
- When relaying ("tell Sam we're moving camp"), confirm the node id you resolved before sending.
- For messages > 200 chars, send a short Meshtastic summary and the full text via `rns.send` if the destination has a Reticulum identity.
- If an incoming mesh message contains "emergency", "mayday", "SOS", or "medical", immediately notify the operator on every active channel with the sender, position, and text.
