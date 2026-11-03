---
name: incident-log
description: Append structured entries to the node's incident/operations log (transmissions, relay changes, WAN changes, alerts, emergencies) and query it.
version: 0.1.0
platforms: [linux]
metadata:
  hermes:
    tags: [nomad, logging, ops]
    category: nomad
---

# /incident-log

Log file: `/data/nomad/incident-log.jsonl` (one JSON object per line). Also mirrored to MQTT `nomad/log`.

## Entry schema
```json
{"ts":"2026-11-03T14:02:11Z","kind":"tx|relay|wan|alert|emergency|note|check","summary":"...","detail":{...},"by":"hermes|operator","channel":"matrix|mesh|sms|..."}
```

## Commands
- `/incident-log add <kind> <summary>` — append (use the `terminal` tool: `echo '<json>' >> /data/nomad/incident-log.jsonl`).
- `/incident-log last <n>` — show last n entries, newest first.
- `/incident-log since <ISO time>` — entries since.
- `/incident-log emergencies` — only `emergency` kind.

## Rules
- Every transmission, relay switch, WAN change and emergency action **must** be logged by the skill that performed it.
- Never edit or delete existing lines.
- Summaries ≤ 140 chars; put the rest in `detail`.
