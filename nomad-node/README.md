# nomad-node

Design and configuration for **NOMAD-X**, an integrated off-grid comms + compute node in a Pelican case, run by a local Hermes Agent.

```
nomad-node/
├── DESIGN.md                  # the design doc — start here; feed it to an AI to be guided step by step
├── OPERATORS-GUIDE.md         # plain-language "you just found this case" guide: what it is, scenarios, hardware list
├── hermes/
│   ├── SOUL.md                # Hermes persona + standing orders (copy to ~/.hermes/SOUL.md)
│   ├── config.example.yaml    # ~/.hermes/config.yaml starting point
│   ├── .env.example           # ~/.hermes/.env variable names (verified against Hermes docs)
│   ├── prompts.md             # reusable operator prompts
│   └── skills/nomad/*/SKILL.md# drop into ~/.hermes/skills/nomad/
└── stack/
    ├── docker-compose.yml     # service stack (starting point; not every service is wired yet)
    ├── nomad-mcp/server.py    # MCP server exposing radio/mesh/sdr/power/net tools to Hermes
    ├── bridges/meshtastic_bridge.py
    ├── firstboot/index.html   # offline first-boot operator's guide for the lid touchscreen (kiosk)
    └── homeassistant/automations.example.yaml
```

To be guided through the build, give an AI assistant `DESIGN.md` and the prompt in its **§0**.
