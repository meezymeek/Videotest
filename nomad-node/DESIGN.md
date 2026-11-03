# NOMAD-X: Integrated Off-Grid Comms & Compute Node

**Status:** Design v0.1 (2026-11-03) — iterate here before buying anything.
**Baseline:** Michael Klements' "Project Nomad" (3D-printed case, Beelink SER9, QNAP 2.5/10G switch, GL.iNet travel router, lid monitor, slide-out keyboard). Keep the form factor; add **power, RF, sensing, and a control plane** so one AI agent (Hermes) can run the whole box.

**Design rule (non-negotiable):** every device must expose a control interface (USB-serial, Ethernet, or GPIO), and every control surface is bridged onto one bus (MQTT + Home Assistant). If a part can't be driven by software, it doesn't go in the case.

---

## 0. How to use this document with an AI assistant

This doc is written so that an LLM (Claude, Hermes itself, etc.) can walk you through the build step by step. Paste the following as your first message, then attach or paste this file:

> You are my build guide for the NOMAD-X project described in the attached DESIGN.md. Work through it **one phase at a time**, in order (Phase 0 → 6). For each phase: (1) list the exact parts and tools needed, (2) give numbered step-by-step instructions with exact commands and config file contents, (3) stop at every **Checkpoint** and ask me to run the acceptance test and report the result before continuing, (4) when something in the doc is marked **VERIFY**, tell me what to measure/check and how, and update your plan based on my answer. Never skip a checkpoint. If I report a failure, debug it with me before moving on. Track which phase and step we're on at the top of every reply.

Items marked **VERIFY** are things I could not confirm from primary sources; measure or check them before purchase.

---

## 1. Goals and non-goals

**Goals**
- Self-contained portable network: Wi-Fi 7 + 2.5/10GbE LAN, works with zero internet.
- Local AI operator (Hermes Agent) that can *act* on hardware: tune radios, send mesh messages, scan bands, transcribe voice channels, shed power loads, answer from offline Wikipedia.
- Multiple comms paths, all reachable by the agent: Wi-Fi/LAN, LoRa mesh, HF/VHF/UHF ham, GMRS, cellular (SMS/data), satellite messaging, Starlink when available.
- Offline knowledge: full English Wikipedia with images + medical/electronics/ham/DIY/survival references + offline maps.
- "Wireless GPU": devices on the case's Wi-Fi get GPU-backed inference (WiCi-style). WiCi One drop-in bay reserved.
- Runs on battery + solar, with the agent able to see and manage power.
- Security/pentest toolkit for **your own networks and authorized engagements**.

**Non-goals (v1)**
- Not weather-sealed while running (needs airflow). Sealed only when closed and powered down.
- Not a plug-and-play product; expect 3D printing, crimping, and config work.

---

## 2. Architecture

```
                 ┌────────────────────────── LID ──────────────────────────┐
                 │  15.6" touch OLED  ──  Hermes dashboard (kiosk)          │
                 └──────────────────────────────────────────────────────────┘
 ANTENNA BULKHEADS (case top wall): HF  VHF/UHF  LoRa  GPS  Wi-Fi x4  Cell x2  Sat
                 ┌───────────────────── 10" RACK (8U) ──────────────────────┐
  1U  RF PATCH   │ SMA/N bulkhead panel → internal pigtails                 │
  1U  ROUTER     │ Banana Pi BPI-R4 (OpenWrt) + Wi-Fi 7 BE14 NIC + 5G modem │
  1U  SWITCH     │ MikroTik CRS310-8G+2S+ (8×2.5G, 2×SFP+)                  │
  2U  COMPUTE    │ NVIDIA DGX Spark (128GB, CUDA)  — or MS-01 + RTX 4000 SFF│
  2U  RADIO      │ Icom IC-705 (HF–UHF, USB/LAN CAT)                        │
  1U  RF BAY     │ 2× RTL-SDR v4, Airspy, Meshtastic node, RNode, GPS,      │
                 │ RockBLOCK, Flipper dock, Alfa Wi-Fi adapter, USB hub     │
  1U  POWER      │ Victron SmartShunt, fuse block, DC-DC rails, USB relays  │
                 └──────────────────────────────────────────────────────────┘
  BASE           │ LiFePO4 12.8V 100Ah │ Victron MPPT 100/30 │ keyboard tray│
  RESERVED BAY   │ 3U for WiCi One (or second GPU sled)                     │

 SOFTWARE BUS:  everything → MQTT (Mosquitto) ← Home Assistant ← Hermes (MCP tools)
```

**Control plane in one sentence:** Home Assistant owns every device (via MQTT, serial integrations, and native integrations), exposes them to Hermes through the **Home Assistant MCP server** and a custom **nomad-mcp** server, and Hermes is reachable through self-hosted channels (Matrix, HA, SMS, email-over-radio, Meshtastic bridge) that work with no internet.

---

## 3. Hardware

### 3.1 Enclosure and rack

| Item | Choice | Notes |
|---|---|---|
| Case | **Pelican 1620** (wheeled) | Interior ≈ 545 × 417 × 318 mm (**VERIFY** against Pelican's current spec sheet). Stood on its long edge with the hinge at top, the lid swings up exactly like the Klements build and holds the screen. The 1620's extra depth over the 1610 (≈318 vs 270 mm) is what makes a 200 mm-deep rack + rear cabling fit. Alternative: **Pelican 1637 Air** (bigger interior, ~40% lighter, less rigid — **VERIFY** rack-mount stiffness). |
| Rack | 10" rack rails (DeskPi RackMate rail pairs or 10" aluminum rack strip) on a 3D-printed/aluminum sub-frame bolted to the case floor | Don't use a full DeskPi T0/T1 cabinet — its outer shell wastes depth. Rails only. 10" rack inner width ≈ 222 mm; equipment ≤ 200 mm deep incl. connectors. |
| Rack frame material | 2020 aluminum extrusion + printed corner brackets | Extrusion also carries the fan mounts and keyboard tray slides. |
| Lid screen | 15.6" 1080p **touch** OLED portable monitor, single USB-C (DP Alt + power) | e.g. ASUS ZenScreen OLED touch / Innocn 15A1F class. Mount with VESA plate on printed lid bracket. |
| Keyboard | Slide-out tray on drawer slides; low-profile keyboard + trackpad (Logitech K400 Plus or a 60% + separate trackpad) | USB-wired, not BT, so it works before the OS is up. |
| Cooling | 2× 120 mm PWM fans (intake low, exhaust high) through printed shrouds in the case walls; vent openings get removable IP-rated plugs for transport | Fans driven by an ESP32 (ESPHome) → HA controls PWM from case temperature. Operate with lid open; HA shuts compute down if the lid-closed sensor trips while hot. |
| Lid sensor | Reed switch on ESP32 | |

### 3.2 Compute — the brain (choose one path)

The compute choice is driven by three constraints: Hermes needs a model with **≥64k context and solid tool calling**; WiCi and most AI tooling assume **CUDA**; everything must fit **≤200 mm deep** and run off **DC**.

| | **Path A: NVIDIA DGX Spark** (recommended) | **Path B: Minisforum MS-01 + RTX 4000 SFF Ada 20GB** (budget/x86) | Path C: Strix Halo 128GB mini PC (GMKtec EVO-X2 / Framework Desktop board) |
|---|---|---|---|
| Size | 150 × 150 × 50.5 mm, 1.2 kg — fits 2U with room | 196 × 189 × 48 mm — 2U, **tight on depth** (ports at rear; mount I/O-forward like Klements) | ~200 mm deep — **VERIFY** fit per model; Framework board is Mini-ITX 170×170 on a shelf |
| Memory for models | 128 GB unified, 273 GB/s | 20 GB VRAM + 96 GB system RAM | 128 GB unified (up to 96 GB to GPU), 256 GB/s |
| CUDA | Yes (ARM64) | Yes (x86) | **No** (ROCm/Vulkan) |
| Models that fit for Hermes | gpt-oss-120b, Qwen3-235B-A22B (Q4), Hermes-4-70B, all at 64k+ ctx | gpt-oss-20b (~13 GB, excellent tool calling), Qwen3-14B/30B-A3B Q4 at 64k ctx | same class as Spark |
| Power | USB-C PD 240 W input; ~100–170 W under load (**VERIFY** measured) | 19 V barrel; ~120–180 W with GPU | 20 V barrel; ~120–140 W |
| DC integration | Needs 12 V → 240 W USB-C EPR supply (rare; see §3.6) | Trivial: 12 V → 19 V DC-DC | Trivial: 12 V → 20 V DC-DC |
| Network | 10GbE RJ45 + Wi-Fi 7 + ConnectX-7 | 2× SFP+ 10G + 2× 2.5G | 5GbE (Framework) / 2.5G |
| Storage | 4 TB NVMe built in | 3× M.2 2280 (2× 4 TB) | 2× M.2 |
| Cost | ~$3,000–4,000 | ~$2,000 (MS-01 + card) | ~$2,000 |
| GPU fit notes | None needed | RTX 4000 SFF Ada is dual-slot low-profile, 70 W, no aux power; MS-01 fits it (community-confirmed, "most powerful GPU you can fit in MS-01"). Minisforum **MS-A2** is single-slot only — needs a cooler mod; avoid. | n/a |

**Decision (2026-11-03): Path A — a GB10 / 128 GB box.** The 128 GB + CUDA combination is what makes a *good* local agent (gpt-oss-120b at full context) and keeps the door open for CUDA-based GPU-over-IP. Path B (MS-01 + RTX 4000 SFF Ada, gpt-oss-20b) stays in the doc only as the fallback if no 128 GB GB10 can be sourced.

**Sourcing a GB10 (read before buying):**
- **Must be the 128 GB model.** NVIDIA launched a **64 GB / 1 TB** DGX Spark at $4,999 on 2026-10-23; it cannot hold gpt-oss-120b (~65 GB) plus 64k context. Do not buy it for this build.
- **Pricing is volatile.** 128 GB Founders Edition: $3,999 at launch (2025-10) → $4,699 (2026-02) → reportedly ~$6,950 (2026-10) during the memory shortage; third-party listings $8k+. Budget $4,700–7,000 and **VERIFY** the price the day you order.
- **OEM twins are the same machine.** The GB10 superchip, 128 GB LPDDR5x, ~150 × 150 × 50 mm chassis, USB-C PD power, and NVIDIA AI software stack ship as: **ASUS Ascent GX10**, **Dell Pro Max with GB10**, **HP ZGX Nano**, **Lenovo ThinkStation PGX**, **MSI EdgeXpert MS-C931**, **Gigabyte AI TOP Atom**, **Acer Veriton GN100**. Buy whichever is in stock; differences are cosmetic plus storage size (1 TB on some — add an external NVMe enclosure over USB4 or use the switch-attached NAS path if so). **VERIFY** the exact dimensions and that the unit you pick ships with 128 GB and the ConnectX-7 / 10GbE port set you need.
- Order it first; it's the long-lead item. Everything else in the BOM is in stock.

### 3.3 Network

| Item | Choice | Why |
|---|---|---|
| Router | **Banana Pi BPI-R4** + **BE14 Wi-Fi 7 NIC**, running **OpenWrt** | 2× SFP+ 10G, 4× 1GbE, 1× 2.5G, **2× mPCIe for cellular modems**, Wi-Fi 7 antenna pigtails → RP-SMA bulkheads (external antennas; Wi-Fi inside a Pelican is useless). Fully scriptable (UCI, ubus, SSH). **VERIFY** BE14 OpenWrt stability on current release. Plug-and-play fallback: **GL.iNet Flint 3** (OpenWrt-based, but check whether antennas are detachable — **VERIFY**). |
| Switch | **MikroTik CRS310-8G+2S+IN** | 8× 2.5G RJ45 + 2× SFP+, RouterOS API, 12–57 V DC input, ~207 mm wide (**VERIFY** it fits 222 mm rack opening; else CRS305-1G-4S+). |
| Cellular | Quectel RM520N-GL (5G, M.2) in the BPI-R4 mPCIe/M.2 slot via adapter, dual SIM | OpenWrt mwan3 handles WAN failover: Starlink → cellular. SMS via `mmcli`/gammu → HA/Hermes SMS channel. |
| Satellite internet | **Starlink Mini** (external, stowed in lid pocket) | 12–48 V DC input; Ethernet → router WAN. gRPC status API → HA. |
| Satellite messaging | **RockBLOCK 9603** (Iridium SBD) | Serial; open API; works anywhere; pay-per-message. Garmin inReach/Zoleo have **no local API** and were excluded. |
| Wi-Fi survey | Alfa AWUS036AXML (Wi-Fi 6E, monitor mode) | Kismet. |

VLANs (OpenWrt): `10 mgmt`, `20 lan` (users), `30 iot` (ESP32s, relays), `40 rf` (SDR/radio hosts if any are IP), `50 guest`, `60 pentest` (isolated). The agent talks to the router over the mgmt VLAN only.

### 3.4 Radio layer

| Function | Hardware | Host interface | Software |
|---|---|---|---|
| HF/VHF/UHF ham | **Icom IC-705** (200 × 84 × 82 mm, 10 W, 13.8 V) | USB (CI-V + audio) and/or Wi-Fi LAN | Hamlib `rigctld`, Direwolf (APRS/packet), JS8Call, FLdigi, WSJT-X, Pat (Winlink), VARA HF (Wine) |
| GMRS/FRS | Quansheng UV-K5 (×2) with programming cable; or Midland MXT275 mobile | USB serial (CHIRP), USB sound card for audio | CHIRP, audio piped to Whisper |
| LoRa mesh (people) | 2× Heltec V3 / RAK WisBlock running **Meshtastic** (one inside the case, one as a roaming node) | USB serial | `meshtastic` Python API → MQTT; `meshtastic_bridge.py` → Hermes |
| LoRa mesh (data) | **RNode** (LilyGo T-Beam flashed with RNode firmware) running **Reticulum** | USB serial | `rnsd`, LXMF, NomadNet — encrypted, routable mesh that can bridge LoRa↔Wi-Fi↔Ethernet. Reticulum needs a host per node; this box is that host. |
| Wideband RX | 2× RTL-SDR Blog v4, 1× Airspy R2 (or SDRplay RSPdx) | USB | OpenWebRX+ (web waterfall for any LAN device), `rtl_433`, `dump1090`, `SoapySDR`, `gr-` scripts |
| TX-capable SDR | HackRF One (optional) | USB | TX only on bands you're licensed for |
| GPS / time | u-blox ZED-F9P or NEO-M9N USB | USB serial | `gpsd` → `chrony` (case = Stratum 1 NTP), position → APRS, mesh, maps, HA |
| Sub-GHz/NFC/IR | Flipper Zero in a printed dock | USB serial | `pyflipper` |
| Audio | 2× USB sound cards (DigiRig Mobile for the IC-705; generic for GMRS) | USB | Direwolf, Whisper |
| Antennas | HF: end-fed half-wave (40–10 m) on a 10 m telescoping mast; VHF/UHF: dual-band mag-mount or Slim Jim; LoRa: 915 MHz 5 dBi; GPS: active puck; Wi-Fi: 4× 2.4/5/6 GHz 6 dBi omnis; Cell: 2× wideband 4G/5G | Bulkhead N (HF/VHF) and SMA/RP-SMA (rest) through the top wall | Label everything. |

**USB topology matters.** Use a **powered 10-port industrial USB hub** (e.g. StarTech ST10 class) with per-port power switching if possible, and pin device paths with udev rules (`/dev/radio-ic705`, `/dev/sdr-0`, `/dev/mesh-0`, `/dev/gps`) so services never grab the wrong device.

### 3.5 Sensing and actuation (the "analog needs a digital handle" layer)

| Item | Purpose | Interface |
|---|---|---|
| ESP32-S3 running ESPHome | Case temp/humidity (BME280), fan PWM, lid reed switch, ambient light, 4× spare GPIO | Wi-Fi/MQTT (native HA) |
| 8-channel USB relay board (Numato / Denkovi) | Hard power-cycle individual devices: IC-705, SDR hub, Starlink, RNode, fans | USB serial → HA switch entities |
| Victron SmartShunt 500A | Battery SoC, current, voltage, time-to-empty | VE.Direct → USB → HA Victron integration |
| Victron SmartSolar MPPT 100/30 | Solar input, charge state | VE.Direct → USB → HA |
| INA226/INA3221 breakouts on each DC rail | Per-rail current (compute, radio, RF bay, router) | I2C → ESP32 → MQTT |
| PTT control | IC-705 via CI-V; GMRS via DigiRig/USB sound card PTT line | Hamlib / GPIO |

With this, the agent can run an automated **comms check**: key the radio, send an APRS beacon, verify it's heard on the SDR, send a Meshtastic ping and wait for the ack, send a RockBLOCK test message, check cellular registration, and report — all without a human touching a knob.

### 3.6 Power

**Budget (watts, typical / peak):**

| Load | Idle | Working | Peak |
|---|---|---|---|
| Compute (Spark) | 25 | 120 | 170 |
| Router + Wi-Fi 7 + modem | 12 | 18 | 25 |
| Switch | 8 | 10 | 12 |
| IC-705 | 3 (RX) | 3 | 30 (10 W TX) |
| RF bay (SDRs, LoRa, GPS, hub) | 6 | 10 | 15 |
| Screen | 0 (off) | 12 | 18 |
| Fans, ESP32, relays | 2 | 6 | 10 |
| Starlink Mini (external, optional) | 0 | 30 | 40 |
| **Total** | **~56** | **~210** | **~320** |

**Battery:** 12.8 V LiFePO4 **100 Ah (1,280 Wh)**, e.g. LiTime/Eco-Worthy 100Ah "mini" (≈ 260 × 170 × 190 mm, ~10 kg — **VERIFY** fit in base). ≈ 6 h at full AI load, ≈ 20 h idle/monitoring. If weight matters, 2× 50 Ah in parallel so one can be left behind.

**Solar:** 200 W foldable panel (2× 100 W, MC4) → Victron SmartSolar 100/30. Expect 600–900 Wh/day in good sun. Case accepts panel input via a weatherproof MC4/SAE bulkhead; also an Anderson PB50 bulkhead for vehicle 12 V / external battery / bench PSU.

**DC distribution (no inverter):**
- 12 V bus → Blue Sea fuse block → rails.
- **Compute power (GB10/Spark).** The Spark is powered *only* over USB-C and negotiates **PD 3.1 EPR at the 48 V profile** (measured ~181 W at 47 V/3.85 A under sustained load; system peak 240 W = ~140 W SoC + ~100 W for ConnectX-7, SSD, and USB-C device budget). There is no 12 V barrel input. Two ways to feed it from the 12 V bus:
  - **v1 (do this first):** a **300 W pure-sine inverter** (e.g. Victron Phoenix 12/375 or Renogy 300 W) on its own relay, feeding the **stock NVIDIA 240 W adapter**. ~10% loss, zero compatibility risk, and the inverter doubles as a shore-style AC outlet for anything else. Idle inverter draw ~5–8 W — switch it off in `eco`.
  - **v2 (optimization):** 12 V → 48 V 300 W boost converter feeding a **USB-C PD 3.1 EPR source module** (48 V/5 A, must advertise AVS). **VERIFY** the module actually negotiates EPR with the Spark before committing — many "240 W" boards are sink-side or cap at 140 W. Saves ~15–20 W over v1.
  - Either way, a **USB-C PD meter** inline (EPR-rated) feeds the `compute` rail reading to HA.
- 12 V → **19 V 10 A** DC-DC only if the Path B mini PC is used instead.
- 12 V → 13.8 V regulated for IC-705 (it wants 13.8 V; don't feed it raw battery on a full charge of 14.4 V — **VERIFY** IC-705 input tolerance; spec says 13.8 V ±15%).
- 12 V → 5 V 10 A rail for USB hub, ESP32s, relays.
- 12 V → switch and router directly (both accept 12 V).
- Everything switchable via the relay board; everything metered.

**Shore power:** 120/230 V → 12 V 30 A PSU (Mean Well LRS-350-12) on the Anderson input; or a Victron Blue Smart IP22 charger. Agent sees "shore power present" via the MPPT/shunt data.

### 3.7 "Wireless GPU" (WiCi) — what's real and what we build

**What WiCi is (arXiv 2608.24204, wici.ai):** a closed system that intercepts the **CUDA user-mode driver API** on a thin client (phone, Pi, laptop), batches/replays calls over Wi-Fi to a "GPU router," and reaches ~80% of native GPU performance for LLM inference. **The server/runtime/driver are not published and cannot be run on your own GPU.** The only way to get the wireless driver-mode today is to buy **WiCi One** (RTX 5060 Ti 16 GB or RTX 5090 32 GB, Wi-Fi 7 4×4 320 MHz, wall-powered, "ships in 8 weeks," Developer Preview Q4 2026, no published dimensions or power draw, USB ports only, unclear whether it acts as an AP or joins your Wi-Fi).

**Design decision:**
1. **Reserve a 3U bay** (≈ 222 w × 133 h × 200 d mm) plus a 12 V → AC inverter tap (or DC mod once its PSU is known) for a WiCi One. Treat as a future module. **VERIFY** dimensions when they publish them.
2. **Build the open equivalent now**, which covers 90% of what people will actually use WiCi One for:
   - **Inference-over-Wi-Fi:** llama.cpp / vLLM on the Spark exposes an **OpenAI- and Ollama-compatible API** (`http://ai.nomad.lan/v1`, `:11434`) — exactly what WiCi One's `http://wici-one.local/v1` offers. Any phone/tablet/laptop app that speaks Ollama/OpenAI uses the case's GPU. mDNS advertises `ai.nomad.lan`.
   - **Driver-mode-over-IP (experimental):** open-source CUDA-over-TCP projects (e.g. `scuda`, rCUDA) let a CUDA app on a Linux client use the case GPU. Expect naive remoting to be far slower than WiCi's batched protocol (the paper measured 97–483× slowdowns naive vs. 80% native with their batching). Put it in the "lab" column, not the "depends on it" column.
   - **Wi-Fi 7 link budget:** the BPI-R4 + BE14 gives the 320 MHz / 4×4 link WiCi assumes. Keep the AI SSID on 6 GHz, dedicated.
3. If WiCi One ships and works, it drops into the bay, joins the `lan` VLAN, and Hermes gets a second inference endpoint via its `/v1` API.

---

## 4. Software stack

OS: **DGX OS** (Ubuntu 24.04-based) on the Spark, or **Ubuntu 24.04 Server** on MS-01. Everything else in Docker Compose (`stack/docker-compose.yml`) on an `nvidia` runtime. Hermes runs **natively** (its installer wants the host), not in a container.

### 4.1 Services

| Service | Role | Port / endpoint |
|---|---|---|
| **Mosquitto** | MQTT bus | 1883 (TLS 8883) |
| **Home Assistant** (container, host network) | Device owner; dashboards; automations; **MCP server** (official HA integration) | 8123 |
| **Node-RED** | Glue flows (radio ↔ MQTT, SMS, Winlink) | 1880 |
| **llama.cpp `llama-server`** (or **vLLM**) | Main LLM for Hermes | 8080 `/v1` |
| **Ollama** | Convenience endpoint for phone/tablet apps (Ollama-protocol) | 11434 |
| **faster-whisper server** | STT for radio channel monitoring | 9000 |
| **Piper TTS** | Voice announcements / radio voice replies | 10200 |
| **nomad-mcp** (custom, FastMCP) | Radio/mesh/SDR/power tools for Hermes | stdio or 7777 |
| **Kiwix-serve** | Offline Wikipedia & references | 8081 |
| **tileserver-gl** + **Protomaps** | Offline maps (OSM) | 8082 |
| **OpenWebRX+** | Browser SDR waterfall | 8073 |
| **Direwolf** | APRS/packet TNC (KISS on 8001) | 8000/8001 |
| **rigctld** (Hamlib) | Rig control daemon for IC-705 | 4532 |
| **Pat** (Winlink) | Email over HF/VHF | 8085 |
| **rnsd** + **LXMF** | Reticulum router for RNode | — |
| **Meshtastic bridge** | Mesh ↔ MQTT ↔ Hermes | — |
| **Conduit** (Matrix homeserver) + **Element Web** | Primary offline chat channel to Hermes | 6167 / 8086 |
| **Mailpit / Postfix+Dovecot** | Local mail (Winlink in/out, Hermes email channel) | 25/143/8025 |
| **gammu-smsd** | SMS via cellular modem | → MQTT |
| **gpsd**, **chrony** | Position + Stratum-1 NTP | 2947 / 123 |
| **Kismet** | Wi-Fi/BT survey | 2501 |
| **Pi-hole + Unbound** | LAN DNS (`*.nomad.lan`), ad-block when online | 53 |
| **Vaultwarden, Gitea, Syncthing, Jellyfin, Nextcloud** | Secrets, code, sync, media, files | various |
| **Prometheus + Grafana + node-exporter + nvidia-exporter** | Metrics | 9090 / 3000 |
| **Caddy** | Reverse proxy with local CA; `https://<svc>.nomad.lan` | 80/443 |

### 4.2 Models

| Path A (Spark, 128 GB) | Path B (20 GB VRAM) |
|---|---|
| **Primary:** `gpt-oss-120b` (MXFP4, ~65 GB) — strong tool use, 128k ctx | **Primary:** `gpt-oss-20b` (MXFP4, ~13 GB), 128k ctx |
| Alt: `Qwen3-235B-A22B-Instruct` Q4 (~125 GB, tight), `Hermes-4-70B` Q4 | Alt: `Qwen3-14B` Q4, `Qwen3-30B-A3B` Q4 |
| Vision: `Qwen3-VL-8B` | Vision: `Qwen3-VL-4B` |
| STT: `faster-whisper large-v3-turbo` | same |
| Embeddings (for RAG over Kiwix): `bge-m3` | same |

`llama-server` must run with `--jinja -c 65536` (Hermes requires ≥ 64k context) and `--parallel 2` or fewer (slots divide context). vLLM: `--enable-auto-tool-choice --tool-call-parser hermes --max-model-len 65536`.

### 4.3 Knowledge pack (Kiwix ZIMs, sizes as of 2026-11)

| Tier | Contents | Size |
|---|---|---|
| **Core** (always) | `wikipedia_en_all_maxi_2026-08` 119 G · `wikipedia_en_medicine_maxi_2026-10` 1.7 G · `mdwiki_en_all_2025-11` 10 G · `wiktionary_en_all_nopic_2026-08` 8.5 G · `wikibooks_en_all_maxi_2026-10` 4.4 G · `wikivoyage_en_all_maxi_2026-09` 1.0 G · `theworldfactbook_en_all_2026-02` 0.4 G | **~145 G** |
| **Survival/field** | `zimgit-post-disaster_en_2024-05` 615 M · `zimgit-medicine_en` 67 M · `zimgit-water_en` 20 M · `zimgit-food-preparation_en` 93 M · `zimgit-knots_en` 27 M · `appropedia_en_all_maxi_2026-02` 555 M · `trueprepper.com_en_all_2026-05` 1.3 G · `survivors_en_all_maxi_2026-09` 131 M · `energypedia_en_all_maxi_2026-06` 763 M · `wikivet.net_en_all_maxi` 54 M · `librepathology_en_all_maxi` 91 M | **~3.7 G** |
| **Engineering/ops** | `electronics.stackexchange.com_en_all_2026-10` 4.0 G · `ham.stackexchange.com_en_all_2026-10` 74 M · `diy.stackexchange.com_en_all_2026-10` 1.9 G · `outdoors.stackexchange.com_en_all_2026-10` 135 M · `security.stackexchange.com_en_all_2026-10` 419 M · `unix.stackexchange.com_en_all_2026-10` 1.2 G · `serverfault.com_en_all_2026-10` 1.5 G · `superuser.com_en_all_2026-10` 3.7 G · `devdocs_en_{python,bash,docker,man}` ~35 M · `restarters_en_all_maxi` 16 M | **~13 G** |
| **Big optional** | `stackoverflow.com_en_all_2026-07` 107 G · `crashcourse_en_all_2026-05` 21 G · `wikiversity_en_all_maxi_2026-11` 2.0 G · `wikispecies_en_all_maxi` 3.3 G | **~133 G** |
| **Total, everything** | | **~295 G** |

Download from `https://download.kiwix.org/zim/` (redirects to `lb.download.kiwix.org`). Also fetch the US Army FM 21-76 / TC 4-02.1 PDFs and your local emergency plans into `/data/library/` for RAG.

**Maps:** Protomaps planet `.pmtiles` (~120 G, **VERIFY** current size) or regional extracts (North America ~25 G). Add USGS topo tiles for your region. Serve to Organic Maps / Gaia-compatible clients and the HA map card.

**Storage plan (4 TB NVMe):** models 200 G · knowledge 300 G · maps 150 G · media 1 T · user data/backups 1 T · headroom.

---

## 5. Hermes Agent integration

Hermes is the single operator. It runs on the compute node, talks to the local model, and gets its hands via MCP. Files in `hermes/` are drop-in starting points.

### 5.1 Install and base config

```bash
# On the compute node (Linux). Internet required for install — do this at home, before the box goes off-grid.
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
source ~/.bashrc
hermes --version
hermes setup            # wizard; choose "Custom endpoint" and point at llama-server
```

`~/.hermes/config.yaml` — see `hermes/config.example.yaml`. Key parts:

```yaml
model:
  provider: custom
  base_url: http://127.0.0.1:8080/v1
  default: gpt-oss-120b
  context_length: 65536
  streaming: true            # set false if llama-server's streaming tool-calls misbehave
terminal:
  backend: local
mcp_servers:
  homeassistant:
    url: http://127.0.0.1:8123/mcp_server/sse
    headers: { Authorization: "Bearer ${HA_TOKEN}" }
  nomad:
    command: /opt/nomad/venv/bin/python
    args: ["/opt/nomad/stack/nomad-mcp/server.py"]
    env: { MQTT_HOST: "127.0.0.1" }
```

Secrets go in `~/.hermes/.env` (`HA_TOKEN=...`), never in `config.yaml`.

### 5.2 GUI

- **Primary GUI:** `hermes dashboard --host 0.0.0.0 --port 9119 --no-open` behind Caddy at `https://hermes.nomad.lan`, basic-auth via `HERMES_DASHBOARD_BASIC_AUTH_USERNAME` / `..._PASSWORD_HASH` / `..._SECRET`. Pages: Chat (embedded TUI), Config, Skills, MCP, Cron, Sessions, Logs, Channels, Pairing.
- **Lid touchscreen:** Chromium kiosk → a Home Assistant dashboard with an embedded Hermes Chat iframe, power/RF status tiles, OpenWebRX waterfall, and map. Touch keyboard via the on-screen keyboard; physical keyboard on the tray.
- **Terminal:** `hermes` TUI over SSH from any laptop.
- Run as a service: `hermes gateway install` (user systemd unit `hermes-gateway`), `sudo loginctl enable-linger $USER`.

### 5.3 Channels (feasible without internet)

| Channel | Transport | Hermes side | Notes |
|---|---|---|---|
| **Matrix** (primary) | Wi-Fi/LAN | Built-in Matrix platform → self-hosted **Conduit** homeserver; `MATRIX_ALLOWED_USERS=@hayden:nomad.lan` | Element on phones/laptops; E2EE; group rooms; works 100% offline. |
| **Home Assistant** | LAN | Built-in HA plugin platform | Talk to Hermes from HA's Assist UI and the lid screen. |
| **API Server / Webhooks** | LAN | Built-in | Used by the bridges below. |
| **Meshtastic** | LoRa | `stack/bridges/meshtastic_bridge.py` → Hermes API server | DM the case's node name; replies ≤ 200 chars/packet. |
| **SMS** | Cellular | gammu-smsd → Node-RED → Hermes API → gammu reply; or Hermes SMS platform if the modem is supported (**VERIFY**) | Works with only a cell tower, no data plan. |
| **Email over radio** | HF/VHF via Winlink (Pat) → local Postfix/Dovecot | Hermes built-in Email platform (IMAP/SMTP to localhost) | Slow (minutes), but global with no infrastructure. |
| **Reticulum/LXMF** | LoRa/any | LXMF bot → Hermes API | Encrypted messaging to the agent over Reticulum. |
| **Telegram / Signal / Discord** | Internet (Starlink/cell) | Built-in | Enabled automatically when WAN is up; `*_ALLOWED_USERS` set. |
| **Voice over radio** (stretch) | GMRS/VHF | Whisper → Hermes → Piper → PTT via relay | Push-to-talk assistant on a simplex channel. Keep within license rules (no encryption on ham bands; ID every 10 min). |

Pairing: unknown users get a one-time code; approve with `hermes pairing approve matrix <CODE>`. Default-deny stays on.

### 5.4 Tools exposed to Hermes (`nomad-mcp`)

| Tool | Does | Backing |
|---|---|---|
| `radio.get_state` / `radio.set_freq(mhz, mode)` / `radio.ptt(on)` | Control IC-705 | Hamlib via rigctld |
| `radio.send_aprs(text)` / `radio.aprs_recent(n)` | APRS beacon/messages | Direwolf KISS |
| `radio.winlink_send(to, subject, body)` / `winlink_sync()` | Email over radio | Pat CLI |
| `mesh.send(text, to=None, channel=0)` / `mesh.nodes()` / `mesh.recent(n)` | Meshtastic | meshtastic Python API |
| `rns.send(dest_hash, text)` | Reticulum/LXMF | lxmf |
| `sdr.scan(start_mhz, stop_mhz, step)` → signal peaks | Band survey | `rtl_power` / SoapySDR |
| `sdr.monitor_start(freq, mode, minutes)` → transcript | Record + Whisper transcribe a channel | rtl_fm/SDR++ headless + faster-whisper |
| `sdr.decode_433()` / `sdr.adsb_nearby()` | Sensors and aircraft | rtl_433 / dump1090 |
| `sat.send(text)` / `sat.inbox()` | Iridium SBD | RockBLOCK serial |
| `power.status()` | SoC, W in/out, time-to-empty, per-rail amps | Victron + INA226 via HA |
| `power.relay(name, on)` / `power.mode("eco"\|"normal"\|"max")` | Switch loads; set policy | USB relay board via HA |
| `net.status()` / `net.wan_failover(prefer)` / `net.clients()` / `net.vlan_isolate(mac)` | Router ops | OpenWrt ubus/SSH |
| `gps.fix()` | Position/time | gpsd |
| `env.status()` | Case temp/humidity/lid/fans | ESPHome via HA |
| `kb.search(query)` / `kb.read(url)` | Offline Wikipedia/refs | kiwix-serve search API |
| `comms.check_all()` | Runs the full comms self-test (see 3.5) and returns a report | composition of the above |

HA's own MCP server additionally exposes every entity (lights, switches, sensors) generically.

### 5.5 Persona, prompts, skills

- `hermes/SOUL.md` — the operator persona and standing orders (safety rules for TX, power policy, honesty about uncertainty).
- `hermes/skills/nomad/*/SKILL.md` — procedural skills: `comms-check`, `radio-ops`, `mesh-ops`, `sdr-monitor`, `power-management`, `net-ops`, `knowledge-lookup`, `incident-log`. Invoke with `/comms-check` etc. from any channel.
- `hermes/prompts.md` — reusable prompts (daily status brief, band-conditions report, "we lost cell, get me a message out" runbook).

Cron (Hermes dashboard → Cron, or `~/.hermes/cron/`): `*/30 * * * *` power + comms brief to Matrix; `0 */6 * * *` Winlink sync when HF conditions allow; `0 7 * * *` daily brief.

---

## 6. Security layer (own networks / authorized engagements only)

- **Kali** in a container/VM on VLAN 60 with the Alfa adapter and HackRF passed through; **Kismet** for Wi-Fi/BT survey; Flipper for sub-GHz/NFC/IR research.
- Everything on `pentest` VLAN is firewalled from `mgmt`, `lan`, and `iot`. Hermes can start/stop these tools but **does not** get autonomous offensive tools — keep a human in that loop.
- Legal: FCC Technician (minimum) for ham TX; GMRS license for GMRS; HackRF TX only on licensed bands; Kismet/Wi-Fi testing only on networks you own or have written authorization for.

---

## 7. Build phases (each ends in a Checkpoint)

### Phase 0 — Bench prototype (no case)
Compute node + switch + router on a bench, shore power. Install OS, Docker, NVIDIA runtime, Hermes, llama-server, HA, Mosquitto, Kiwix with the `mini` Wikipedia (13 G) as a stand-in.
**Checkpoint 0:** From a phone on the case Wi-Fi, (a) open `https://hermes.nomad.lan` and get a chat reply from the local model, (b) ask it "what's the battery state" and get an honest "no power telemetry yet," (c) open Kiwix and read an article. `hermes doctor` is clean.

### Phase 1 — Control bus and power
Build the 12 V distribution, Victron shunt + MPPT, relay board, ESP32 sensors. Integrate into HA; expose via HA MCP + `nomad-mcp power.*`.
**Checkpoint 1:** Hermes answers `power.status()` with real SoC and watts; `/power eco` turns off the screen and SDR rail via relays; disconnect shore power and the agent reports "on battery, N hours remaining."

### Phase 2 — RF bay
GPS, 2× RTL-SDR, Meshtastic node, RNode, RockBLOCK, USB hub, udev rules. OpenWebRX, rtl_433, dump1090, gpsd/chrony, Meshtastic bridge, rnsd.
**Checkpoint 2:** From Matrix: `/sdr scan 144 148` returns peaks; DM the case node from a handheld Meshtastic and Hermes replies over the mesh; `gps.fix()` returns a position; chrony shows the case as Stratum 1; RockBLOCK test message arrives in the Rock7 portal.

### Phase 3 — Ham/GMRS
IC-705 + DigiRig; rigctld, Direwolf, Pat, JS8Call. GMRS radios + sound card. Whisper monitoring.
**Checkpoint 3:** `radio.send_aprs("NOMAD test")` is heard on aprs.fi (when online) and on the local SDR; `winlink_send` to your own email arrives via a gateway; `sdr.monitor_start(146.52, "fm", 5)` returns a transcript of a test call you make from a handheld; `comms.check_all()` passes.

### Phase 4 — WAN and channels
Cellular modem, Starlink Mini, mwan3 failover, gammu SMS, Conduit/Element, Hermes gateway with Matrix/HA/SMS/Email/Telegram platforms and pairing.
**Checkpoint 4:** Pull the Starlink cable → traffic fails to cellular within 30 s and Hermes posts "WAN failover: cellular" to Matrix; text the case's SIM from your phone and get a reply from Hermes; with WAN down, Matrix still works.

### Phase 5 — Case integration
Pelican 1620, rack frame, bulkheads, lid screen, keyboard tray, fans, cable dressing, battery mounting, transport plugs. Full knowledge pack and maps.
**Checkpoint 5:** 2-hour full-load soak with lid open: case temp < 45 °C at the compute inlet; close the lid while hot → HA automation shuts compute down within 60 s; drop test of the closed case (your call on height) → everything boots.

### Phase 6 — Field test and WiCi bay
48-hour off-grid run on solar. Phone/tablet apps pointed at `http://ai.nomad.lan:11434` (Ollama) and `/v1`. When WiCi One ships: mount in the reserved bay, add to `lan`, register `http://wici-one.local/v1` as a second Hermes provider.
**Checkpoint 6:** Daily brief arrives on Matrix every morning for 2 days with no intervention; battery never below 20%; a Pi 5 on the Wi-Fi runs a 20B-class model via the case GPU at > 20 tok/s.

---

## 8. Bill of materials (summary; prices rough, USD, 2026-11)

| Group | Items | Est. |
|---|---|---|
| Enclosure | Pelican 1620, rack rails, 2020 extrusion, prints, drawer slides, fans, bulkheads, Anderson/MC4 inlets | 600 |
| Compute | GB10 128 GB box (DGX Spark or OEM twin; Path A) **or** MS-01 + RTX 4000 SFF Ada + 2× 4 TB NVMe (Path B fallback) | 4,700–7,000 / 2,300 |
| Display/input | 15.6" touch OLED, keyboard/trackpad | 350 |
| Network | BPI-R4 + BE14 + antennas, CRS310 switch, RM520N modem + adapter, cables/DACs | 650 |
| Radio | IC-705, DigiRig, antennas + mast, 2× UV-K5, 2× RTL-SDR v4, Airspy R2, 2× Heltec V3, T-Beam (RNode), ZED-F9P GPS, RockBLOCK + Iridium plan, Flipper Zero, HackRF (opt.) | 2,400 |
| Power | 100 Ah LiFePO4, Victron MPPT 100/30 + SmartShunt, 200 W panel, 300 W pure-sine inverter (Spark), DC-DCs, fuse block, relay board, Mean Well shore PSU, EPR PD meter | 1,300 |
| Sensing/misc | ESP32-S3, BME280, INA226s, powered USB hub, industrial cabling | 200 |
| Optional | Starlink Mini (+ plan), Alfa AWUS036AXML, WiCi One (bay reserved) | 600 + 2,600 |
| **Total (Path A, no optionals)** | | **~10,200–12,500** (dominated by GB10 price on the day) |
| **Total (Path B, no optionals)** | | **~7,800** |

---

## 9. Open questions (resolve before ordering)

1. ~~Compute path~~ — **Decided: GB10 128 GB (Spark or OEM twin).** Remaining: which OEM box is actually obtainable at a sane price, and whether it ships with 4 TB or 1 TB (changes the storage plan in §4.3).
2. **Pelican 1620 vs 1637 Air** — measure rack depth with the screen in the lid. Need ≥ 200 mm bay depth + 30 mm cable bend.
3. **BPI-R4 + BE14 OpenWrt maturity** vs Flint 3 convenience (and whether Flint 3 antennas detach).
4. **WiCi One** physical size/power — ask the vendor; adjust the reserved bay.
5. **Hermes SMS/HA/Email platform specifics** — confirm env var names per platform in the Hermes messaging docs during Phase 4.
6. Battery weight budget — is ~30 kg total acceptable for your use (wheels help), or go 50 Ah?

---

## 10. Sources consulted (2026-11-03)

- Hermes Agent docs: install, configuration, providers, messaging, skills, MCP, web dashboard — hermes-agent.nousresearch.com/docs; github.com/NousResearch/hermes-agent
- WiCi: arXiv 2608.24204; wici.ai (product, technology, developers); github.com/wici-ai/inferssd
- Kiwix ZIM listings: download.kiwix.org/zim/{wikipedia,other,stack_exchange,wiktionary,wikibooks,wikiversity,wikivoyage,devdocs}
- Minisforum MS-01/MS-A2 GPU fit: williamlam.com (RTX 4000 Ada in MS-A2 with cooler mod), techenclave MS-01 threads, Notebookcheck MS-A2 review
- DGX Spark vs Strix Halo: The Register (2025-12), Liliputing, Notebookcheck
- DGX Spark pricing/64 GB variant: The Register (2026-10-02), ServeTheHome, Notebookcheck; power: NVIDIA developer forum "DGX Spark Power Clarification", ChargerLAB adapter teardown/compatibility tests
- DeskPi RackMate dimensions: DeskPi/52Pi listings
- Meshtastic↔HA: meshtastic2hass (PyPI), homeassistant-meshtastic
