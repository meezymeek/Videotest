# NOMAD operator prompts

Reusable prompts for the Hermes agent (or any LLM with the nomad tools). Paste or bind to cron.

## Daily brief (cron 0 7 * * * → Matrix)
> Produce the morning brief. Read power.status, env.status, net.status, gps.fix, mesh.nodes, and the last 12 h of the incident log. Report: battery SoC and forecast hours at current load; solar yield since midnight; which WAN paths are up; mesh nodes heard in the last 12 h; any device that failed a comms check; case temperature; anything you changed overnight. Under 120 words. If anything is below the thresholds in SOUL.md, lead with that.

## Comms self-test
> Run /comms-check and give me the pass/fail table. For every failure, state the most likely cause and the one command you'd run next.

## "Get a message out" runbook
> I need this message delivered to <recipient> as fast as possible and I don't know which links work: "<message>". Check net.status and power.status, then try paths in this order, stopping when one is confirmed delivered: cellular SMS, Telegram (if WAN), Winlink email, RockBLOCK, Meshtastic broadcast asking any node with internet to relay. Report each attempt with timestamp and result.

## Band conditions
> Scan 3.5–30 MHz in 10 kHz steps with sdr.scan, then 144–148 and 420–450 MHz. Report the strongest 10 signals with likely identification (broadcast, amateur, digital mode, noise). Tell me which ham band is most likely to work for a 10 W Winlink session right now and why.

## Channel monitor
> Monitor 146.520 MHz FM for the next 30 minutes with sdr.monitor_start, transcribe everything, and alert me on Matrix immediately if you hear "mayday", "emergency", "medical", or our callsign. At the end, summarize traffic.

## Power planning
> We're staying here 3 more days. Using today's solar yield and the current load profile, propose a power plan: which loads to keep, an eco schedule, and expected SoC at the end of each day. Apply the plan only after I approve.

## Knowledge lookup (field)
> Using only offline sources (kb.search, local docs), answer: <question>. Cite the article title and section. If the offline sources don't cover it, say so plainly.

## New node onboarding
> A new device wants to join the network: <description>. Decide the VLAN per DESIGN.md §3.3, create its DHCP reservation and DNS name under nomad.lan via net tools, and if it exposes a control interface, propose the HA entity definition and MQTT topics for it. Show me the config before applying.
