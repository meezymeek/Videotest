# NOMAD-X — First-Time Operator's Guide

*Print this. Keep a copy in the lid pocket. If you found this case and don't know what it is, start here.*

---

## If you have 60 seconds

**What this is:** A portable computer, library, radio room, and power plant in one wheeled case. It works with **no internet, no cell service, and no wall power.** It has its own Wi-Fi, its own AI assistant (named **NOMAD**), and several ways to send messages to the outside world when nothing else works.

**To turn it on:**
1. Stand the case on its long edge (wheels to the side), unlatch, and lift the lid. The screen is in the lid.
2. Flip the red **MAIN** switch on the power panel (bottom of the rack). Lights come on.
3. Wait about 2 minutes. The screen shows a dashboard with battery, radios, and a chat box.
4. Type or tap in the chat box: **"Hello, what can you do?"** NOMAD will answer and tell you the state of the box.

**To get help from the outside world:** Type **"emergency"** in the chat box and then what's wrong. NOMAD will send your location and message on every link it has (satellite, cell text, radio, mesh) and tell you what got through.

**To turn it off:** Type **"shut down"** in the chat, wait for the screen to go black, then flip **MAIN** off. Close the lid only after it's off and cool.

**Don't:** run it with the lid closed; let it sit in direct sun; press the transmit button on the radio unless NOMAD or a licensed operator tells you to.

---

## 1. What is this thing?

Think of it as four things fused together:

| Everyday equivalent | What's in the case | Why it matters |
|---|---|---|
| A good laptop + a small server | A compact AI computer ("the brain") | Runs the assistant, stores everything, serves the Wi-Fi apps |
| A library | Offline copies of Wikipedia, medical references, repair guides, maps, survival manuals | Answers questions when there's no Google |
| A ham radio shack + a phone + a satellite messenger | HF/VHF/UHF radio, walkie-talkies, long-range "mesh" radios, cell modem, satellite text modem | Many different ways to reach people, so at least one works |
| A solar generator | Big lithium battery + solar input + power management | Keeps everything running for days without wall power |

Tying it together is **NOMAD**, an AI assistant that lives inside the box (not in the cloud). It can see the battery, hear the radios, send messages, look things up, and manage the power. You talk to it by typing on the screen, by chatting from your phone on the case's Wi-Fi, or — if you're away from the case — by texting it over the mesh radio or a cell text.

**What it is not:** It is not a phone, not internet (unless a Starlink dish or a cell tower is available), and not waterproof while running. It's a base station: set it up, run it with the lid open, close it to move.

---

## 2. What it's for

- **Off-grid stays and expeditions.** A camp with Wi-Fi, maps, an encyclopedia, a weather radio, and a way to message home.
- **Disasters and outages.** When cell, internet, and power are down, this still works and can relay messages for a group.
- **Remote work sites.** Local network, file sharing, documentation, radio comms, and a smart assistant for a crew.
- **A mobile radio/communications post.** Monitor channels, relay traffic, run message email over the airwaves.
- **Tinkering.** It's also a lab: software-defined radios, a Wi-Fi survey kit, and a GPU you can use from any device on the case's Wi-Fi.

---

## 3. A tour of the box

Stand it up, open the lid, and you'll see a stack of slim boxes in a small rack. From top to bottom:

```
 LID:    touch screen (this is where you talk to NOMAD)
 ┌──────────────────────────────────────────────┐
 │ RF PANEL    antenna jacks, labeled HF/VHF/   │  ← where antennas plug in
 │             LORA/GPS/CELL/SAT                │
 │ ROUTER      the Wi-Fi/network box            │  ← makes the "NOMAD" Wi-Fi (with the puck outside)
 │ SWITCH      a row of network ports           │  ← plug laptops in by cable here
 │ BRAIN       the AI computer                  │  ← runs everything
 │ RADIO       Icom IC-705 (has its own screen) │  ← ham radio, HF to UHF
 │ RF BAY      small radios: mesh, SDR, GPS,    │  ← mostly automatic
 │             satellite modem, Flipper         │
 │ POWER PANEL MAIN switch, meter, fuses        │  ← on/off and battery readout
 └──────────────────────────────────────────────┘
 BESIDE THE RACK: the battery, solar controller, inverter
 BOTTOM:          slide-out keyboard tray
 OUTSIDE:         Wi-Fi puck (mounts on the lid), antennas, solar panel, mast
```

**Things you'll touch:** the MAIN switch, the screen, the keyboard tray, the antenna jacks, the solar/vehicle power inlets on the side, and the Wi-Fi puck. Everything else is meant to be left alone.

---

## 4. How you talk to it

| You are… | Use this | How |
|---|---|---|
| At the case | **The touch screen** | Tap the chat box, type or use the on-screen keyboard. The keyboard tray slides out from the bottom. |
| Nearby with a phone/laptop | **The case's Wi-Fi** (network name `NOMAD`, password on the lid label) | Open the **Element** chat app (or go to `https://hermes.nomad.lan` in a browser) and message **NOMAD**. Works with no internet. |
| Out of Wi-Fi range (up to several miles, line of sight) | **A mesh handheld** (the small radios with screens in the lid pocket) | Open the Meshtastic app on your phone, pair with the handheld, and send a direct message to the node named **NOMAD**. Replies are short (text-message length). |
| Anywhere with cell signal | **Text message** | Text the case's phone number (on the lid label). NOMAD replies by text. No data plan needed, just a signal. |
| When internet is up (Starlink or cell data) | **Telegram** | Message the NOMAD bot. |
| Over the ham radio (slow, global) | **Email via radio (Winlink)** | For licensed operators; NOMAD can send and receive email over HF with no infrastructure at all. |

**Tip:** NOMAD understands plain English. "How much battery is left?", "Send Sam a message that we're moving camp", "What's the weather forecast on the radio?", "How do I treat a burn?" all work.

---

## 5. Meet NOMAD

NOMAD is the assistant. It runs entirely inside the box, so it works with no internet and nothing you say leaves the case.

**What it can do**
- Tell you the state of everything: battery, solar, which links are working, temperature, location.
- Send messages for you on any link: mesh, text, satellite, radio, email-over-radio.
- Listen to radio channels and tell you what it heard (it transcribes voice).
- Scan the airwaves and tell you what's active (weather radio, repeaters, aircraft nearby).
- Answer questions from the offline library and tell you *where* the answer came from.
- Manage power: turn things off to stretch the battery, warn you before it runs out.
- Run a full self-test of every link ("comms check").
- Keep a log of everything it did.

**What it won't do**
- It won't transmit on the ham radio unless you (a licensed operator) tell it to, and only on allowed frequencies.
- It won't pretend. If a link is down or it doesn't know, it says so.
- It won't let the battery die: below 30% it goes into power-saving mode and tells you; below 15% it shuts off non-essentials by itself.
- It won't do anything with the security/pentest tools on its own.

**Shortcuts** you can type in any chat: `/comms-check` (test all links), `/power eco` (save power), `/power normal`, `/sdr-monitor`, `/knowledge-lookup`, `/incident-log last 10`.

---

## 6. Scenarios

Each one: what's happening, what you do, what happens, and how it works underneath.

### 6.1 "I just found this and need to know if it works"
**Do:** Turn it on (see the 60-second section). When the dashboard appears, type `/comms-check`.
**What happens:** In about two minutes NOMAD posts a table: GPS ✓, Wi-Fi ✓, mesh ✓, radio ✓, cell ✗ (no signal), satellite ✓, battery 84%, and a one-line verdict like "GREEN — all links except cell."
**How it works:** NOMAD sends a tiny test message on each link and listens for the echo or acknowledgement — a mesh ping to the spare handheld, a radio beacon it hears on its own receiver, a satellite test packet — and reports what came back.

### 6.2 "Someone is hurt and we have no phone signal"
**Do:** Type **"emergency: broken leg, two people, need evacuation"** in the chat. If the box is off, turn it on first — it's ready in two minutes.
**What happens:** NOMAD grabs the GPS position and immediately sends the message on every link at once: satellite text (works anywhere with sky view), cell text (in case a tower is barely reachable), mesh broadcast (reaches any other mesh users nearby), radio beacon (APRS — ham operators and the internet gateway network can see it), and email-over-radio. It then tells you: "Satellite: delivered. Cell: no signal. Mesh: 1 node acknowledged. Radio: sent, not confirmed." It keeps trying the failed ones.
**How it works:** The satellite modem (Iridium) talks to satellites directly — no towers needed, just open sky. That's the one that almost always works. The others are backups. Meanwhile, use the first-aid section of the offline library: "How do I splint a lower leg fracture?"

### 6.3 "Is there any weather coming?"
**Do:** Ask **"What's the weather forecast?"**
**What happens:** NOMAD tunes one of its receivers to the NOAA weather radio frequency, listens for three minutes, transcribes it, and gives you the summary: "Storm warning for the county after 6 pm, winds 40 mph."
**How it works:** The case has small software radios that can tune anywhere. NOMAD picks the strongest weather station, records the audio, and runs speech-to-text on it.

### 6.4 "Tell the group we're moving camp"
**Do:** Say **"Tell everyone on the mesh we're moving camp to the north ridge at 3 pm."**
**What happens:** NOMAD broadcasts a short message on the mesh network. Anyone carrying one of the mesh handhelds (or a phone paired to one) gets it, miles away, with no cell service. NOMAD tells you who acknowledged.
**How it works:** Mesh radios are tiny long-range radios that pass messages to each other, hop by hop. The case is one node; each handheld is another.

### 6.5 "I need to look something up and there's no internet"
**Do:** Ask the question. "How do I purify water with bleach?" "What does this snake look like?" "How do I fix a flooded carburetor?"
**What happens:** NOMAD answers and cites where it came from, like *[Water: Emergency Disinfection § Household bleach]*. You can also open the library yourself: on any device on the Wi-Fi, go to `http://library.nomad.lan` for Wikipedia, medical references, repair guides, and more, or `http://maps.nomad.lan` for maps.
**How it works:** The box stores a full copy of English Wikipedia (with pictures), a medical encyclopedia, electronics/DIY/ham-radio Q&A sites, and disaster/water/food/knots field manuals — about 300 GB of reference — plus street and topo maps for the region. NOMAD searches that instead of the web.

### 6.6 "The battery is getting low"
**Do:** Nothing, usually. Or ask **"How long will the battery last?"**
**What happens:** NOMAD watches the battery constantly. At 30% it switches to power-saving mode on its own (screen dims, extra radios off) and tells you. At 15% it turns off everything non-essential and keeps only the mesh, GPS, network, and radio receiver alive, so you can still get a message out. It will tell you "about 6 hours at current use" and suggest what to turn off.
**How it works:** A battery monitor reports exact charge and current to the box. NOMAD controls a bank of power switches (relays) for each device. Rules are built in; you can override them: "Keep the screen on."

### 6.7 "It's sunny — are we charging?"
**Do:** Unfold the solar panel, point it at the sun, plug it into the **SOLAR** inlet on the side of the case. Ask **"Are we charging?"**
**What happens:** "Solar in: 140 W. Battery 62% and rising. Full in about 4 hours." Every half hour NOMAD posts a short power report to the chat.
**How it works:** A solar charge controller inside manages the panel and reports to the box. The case can also charge from a vehicle's 12 V outlet or a wall outlet via the **DC IN** inlet.

### 6.8 "The internet is back / we have Starlink"
**Do:** Plug the Starlink Mini into the **WAN** port on the switch (and its power into the aux outlet). Or do nothing if there's cell data.
**What happens:** Within a minute NOMAD posts "WAN: Starlink is up." Everyone on the case's Wi-Fi now has internet. Telegram starts working. NOMAD can fetch news or current info if you ask. If Starlink drops, it fails over to cellular automatically and tells you — and warns that cellular data is metered.
**How it works:** The router watches both links and switches between them. The whole camp shares the connection through the case's Wi-Fi.

### 6.9 "Monitor the radio and wake me if someone calls for help"
**Do:** Say **"Monitor 146.52 tonight and alert me on the mesh if you hear 'mayday' or 'emergency.'"**
**What happens:** NOMAD listens all night, transcribes everything, and if a keyword shows up it pings your mesh handheld immediately with what was said. In the morning: "Quiet night. Two check-ins at 02:10 and 04:45, no distress calls."
**How it works:** One of the software radios records the channel; speech-to-text runs on the box's GPU; keyword hits trigger a message on whichever link reaches you.

### 6.10 "Send an email when there's no internet at all"
**Do (licensed ham operator):** Say **"Send a Winlink email to my wife: we're safe, at the cabin, back Tuesday."** Then raise the HF antenna (the long wire on the telescoping mast).
**What happens:** NOMAD writes the email, picks a radio frequency likely to work right now, tunes the Icom radio, and transmits the email over shortwave to a volunteer gateway station that puts it on the real internet. It usually takes a few minutes. Replies come back the same way next time it checks.
**How it works:** Winlink is a worldwide amateur-radio email system. The box has a 10-watt HF radio that can reach hundreds or thousands of miles depending on conditions. NOMAD handles the radio tuning and the connection.

### 6.11 "A new person wants on the Wi-Fi"
**Do:** Give them the network name and password from the lid label. For more control: **"Add Alex's phone as a guest."**
**What happens:** They get Wi-Fi, the library, the maps, and chat with NOMAD. Guests are kept separate from the case's own controls.
**How it works:** The router keeps separate "lanes" (VLANs) for the box's internals, trusted users, guests, and gadgets, so a guest can't accidentally reach the radio controls.

### 6.12 "What's flying overhead?" / "Is anyone's car key nearby?" (curiosity)
**Do:** Ask **"What aircraft are nearby?"** or **"What sensors are transmitting around here?"**
**What happens:** A list of aircraft with callsigns, altitude, and distance (from their transponders), or a list of nearby wireless sensors (weather stations, tire-pressure sensors, doorbells).
**How it works:** The software radios decode public, unencrypted broadcasts. Receive-only; nothing is transmitted.

### 6.13 "I want to use the AI on my own laptop/tablet"
**Do:** On the case's Wi-Fi, point any app that supports "Ollama" or "OpenAI-compatible" models at `http://ai.nomad.lan:11434` or `http://ai.nomad.lan:8080/v1`.
**What happens:** Your device uses the box's GPU as if it were a cloud AI service — just local and private.
**How it works:** The brain runs large language models on its 128 GB of memory and shares them over Wi-Fi 7. (A dedicated "wireless GPU" module can be added in the spare bay later.)

### 6.14 "It's hot out and the fans are loud"
**Do:** Shade the case (tarp, awning, vehicle). Ask **"How hot is it inside?"**
**What happens:** NOMAD reports the temperature at the computer's air intake. Above its comfort range it dims performance and tells you; if it gets too hot it switches to eco mode by itself.
**How it works:** The computer is the one part that doesn't like heat (its comfort range tops out around 30 °C / 86 °F). Temperature sensors drive the fans, and rules protect it. The case must be **open** while running — closing it while hot triggers an automatic shutdown.

### 6.15 "We're done — pack it up"
**Do:** Type **"shut down."** Wait for the screen to go black and the fans to stop. Flip MAIN off. Unplug antennas and solar, cap the jacks, fold the Wi-Fi puck into the lid pocket, slide the keyboard in, close and latch.
**What happens:** Everything saves and stops cleanly. The battery holds its charge for months.
**How it works:** The shutdown command stops services in order so no data is lost. The battery's own protection circuit keeps it safe in storage.

---

## 7. Routines

**Setting up at a new site (10 minutes)**
1. Stand the case on firm, shaded ground. Open it.
2. Mount the Wi-Fi puck on the lid top (it clips on) and connect its cable.
3. Screw on the antennas: GPS puck, mesh whip, VHF/UHF whip. If a licensed operator is present and HF is needed, raise the mast and wire antenna.
4. Unfold the solar panel if there's sun; plug into SOLAR.
5. MAIN on. Wait for the dashboard. Run `/comms-check`.
6. Ask NOMAD to post a status every hour: "Hourly status to the chat, please."

**Daily**
- Morning: read NOMAD's daily brief (it posts one at 7 am).
- Keep the panel pointed at the sun. Check the battery number on the power panel occasionally.
- Night: ask "Will we make it to sunrise on battery?" and follow its advice.

**Moving**
- Shut down (6.15). Never travel with it running. The case rolls on its wheels in the normal orientation; stand it on edge only to operate.

---

## 8. Hardware list (plain language)

**The case and frame**
- Pelican 1637 Air wheeled case (the shell). Inside: a small 10-inch rack frame, a slide-out keyboard tray, two quiet fans, sealed plugs for the vents when closed.
- 15.6" touch screen in the lid; compact keyboard with trackpad in the tray.

**The brain**
- NVIDIA DGX Spark (or an identical ASUS/Dell/HP/Lenovo/MSI model): a palm-sized AI computer with 128 GB of memory and a 4 TB drive. Runs NOMAD, the library, maps, and all the radio software.

**Network**
- Banana Pi BPI-R4 router (the traffic cop; also holds the 5G cell modem and SIM cards).
- GL.iNet Flint 3 Wi-Fi 7 puck (mounts outside the case; makes the `NOMAD` Wi-Fi).
- MikroTik 10-port switch (wired ports for laptops and gear).
- Optional: Starlink Mini dish (satellite internet when you have it).

**Radios**
- Icom IC-705: a 10-watt ham radio covering shortwave through UHF, with a USB connection so NOMAD can control it. Needs a licensed operator to transmit.
- Two Quansheng UV-K5 handhelds (GMRS/FRS family radios; GMRS needs a no-test license).
- Three Meshtastic mesh radios (one in the case, two handhelds) — license-free text messaging for miles.
- One RNode/Reticulum radio — an encrypted mesh for private data.
- Software-defined radio receivers (two RTL-SDR, one Airspy): listen to almost anything, transmit nothing.
- RockBLOCK Iridium satellite modem: short text messages from anywhere on Earth with sky view (subscription required).
- GPS receiver: position and precise time for everything.
- Flipper Zero: a pocket gadget for reading key fobs, NFC cards, and infrared — a tinkering tool.
- Antennas: wire antenna + 10 m telescoping mast for shortwave; whips for VHF/UHF, mesh, cell, and Wi-Fi; a GPS puck. Each plugs into a labeled jack on the RF panel.

**Power**
- 12 V, 100 Ah lithium (LiFePO4) battery — about 1.3 kWh, roughly 6 hours of heavy AI use or a day of monitoring.
- 200 W folding solar panel; Victron solar charge controller and battery monitor (NOMAD reads these).
- Small inverter that powers the brain's own adapter; DC converters for everything else; a fuse panel; a bank of software-controlled power switches.
- Inlets on the side: SOLAR (MC4), DC IN (Anderson, for vehicle 12 V or the wall supply), and a wall charger.

**Sensors and small parts**
- A tiny ESP32 board with temperature/humidity sensors, the lid switch, and fan control.
- A powered USB hub that everything in the RF bay plugs into.
- A Wi-Fi survey adapter and a Kali Linux toolkit (for authorized security testing only).

---

## 9. Safety and legal, in brief

- **Heat:** Operate with the lid open, in shade. The brain's comfort range is about 5–30 °C (41–86 °F).
- **Water:** Closed and off, the case is weatherproof. Open and running, it is not. If it rains, shut down and close it.
- **Electricity:** The battery can deliver a lot of current. Don't open the power panel or bypass fuses.
- **Radio licenses (US):** Transmitting on the ham radio (IC-705) requires an FCC amateur license — Technician at minimum, General for most shortwave email. GMRS handhelds need a GMRS license (no test). Mesh radios, satellite modem, cell, Wi-Fi: no license. Listening is always legal.
- **Transmitting etiquette:** NOMAD will only transmit on the ham radio when a licensed operator asks, and it identifies with that operator's callsign. In a genuine emergency, FCC rules allow any means necessary to get help — use the `emergency` command.
- **Security tools:** Only on networks you own or have written permission to test.
- **Privacy:** Nothing you say to NOMAD leaves the case unless you ask it to send a message. There is no cloud.

---

## 10. Words you'll see

- **NOMAD** — the assistant inside the box. **Hermes** — the software it's built on.
- **Mesh / Meshtastic** — license-free long-range text radios that relay for each other.
- **HF / VHF / UHF** — radio bands: shortwave (long distance, needs a big antenna), and two shorter-range bands (local, small antenna).
- **APRS** — a ham-radio system for broadcasting position and short messages.
- **Winlink** — email sent over ham radio.
- **SDR** — a "software-defined radio," a receiver that can tune to anything under software control.
- **SoC / eco mode** — battery state of charge; a power-saving mode.
- **WAN** — the outside internet connection (Starlink or cell). **LAN / Wi-Fi** — the case's own network.
- **Kiwix / the library** — the offline copy of Wikipedia and other references.
- **RF panel** — the row of antenna jacks.
