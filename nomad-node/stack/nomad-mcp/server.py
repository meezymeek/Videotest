"""nomad-mcp: MCP server exposing NOMAD-X hardware tools to Hermes.

Skeleton. Each tool is a thin wrapper over an existing daemon (rigctld, Direwolf,
meshtastic, rtl_power, gpsd, Home Assistant). Unimplemented paths raise so the
agent reports honestly instead of pretending.

Run: /opt/nomad/venv/bin/python server.py   (stdio transport, launched by Hermes)
Deps: pip install "mcp[cli]" paho-mqtt meshtastic httpx gpsd-py3
"""

from __future__ import annotations

import json
import os
import socket
import subprocess
import time
from datetime import datetime, timezone

import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("nomad")

MQTT_HOST = os.environ.get("MQTT_HOST", "127.0.0.1")
RIGCTLD = os.environ.get("RIGCTLD", "127.0.0.1:4532")
KIWIX_URL = os.environ.get("KIWIX_URL", "http://127.0.0.1:8081")
HA_URL = os.environ.get("HA_URL", "http://127.0.0.1:8123")
HA_TOKEN = os.environ.get("HA_TOKEN", "")
LOG_PATH = os.environ.get("NOMAD_LOG", "/data/nomad/incident-log.jsonl")


def _log(kind: str, summary: str, **detail) -> None:
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "kind": kind,
        "summary": summary[:140],
        "detail": detail,
        "by": "hermes",
    }
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")


def _ha(method: str, path: str, **payload):
    r = httpx.request(
        method,
        f"{HA_URL}/api/{path}",
        headers={"Authorization": f"Bearer {HA_TOKEN}"},
        json=payload or None,
        timeout=15,
    )
    r.raise_for_status()
    return r.json() if r.content else {}


def _ha_state(entity_id: str):
    return _ha("GET", f"states/{entity_id}")


def _rigctl(cmd: str) -> str:
    host, port = RIGCTLD.split(":")
    with socket.create_connection((host, int(port)), timeout=5) as s:
        s.sendall((cmd + "\n").encode())
        return s.recv(4096).decode().strip()


# ---------------------------------------------------------------- power ----
@mcp.tool()
def power_status() -> dict:
    """Battery SoC, volts, net amps, solar/shore watts in, load watts out, per-rail watts, relay states, mode."""
    ids = {
        "soc_pct": "sensor.nomad_battery_soc",
        "volts": "sensor.nomad_battery_voltage",
        "amps_net": "sensor.nomad_battery_current",
        "watts_in_solar": "sensor.nomad_solar_watts",
        "watts_out": "sensor.nomad_load_watts",
        "time_to_empty_h": "sensor.nomad_time_to_go",
        "mode": "input_select.nomad_power_mode",
    }
    out = {}
    for k, eid in ids.items():
        try:
            out[k] = _ha_state(eid)["state"]
        except Exception as e:  # noqa: BLE001
            out[k] = f"unavailable ({e.__class__.__name__})"
    out["relays"] = {}
    for name in ["ic705", "sdr_hub", "rnode", "starlink", "screen", "fans_boost", "aux1", "aux2"]:
        try:
            out["relays"][name] = _ha_state(f"switch.nomad_relay_{name}")["state"]
        except Exception:  # noqa: BLE001
            out["relays"][name] = "unavailable"
    return out


@mcp.tool()
def power_relay(name: str, on: bool) -> str:
    """Switch a device relay on/off. Names: ic705, sdr_hub, rnode, starlink, screen, fans_boost, aux1, aux2."""
    _ha("POST", f"services/switch/turn_{'on' if on else 'off'}", entity_id=f"switch.nomad_relay_{name}")
    _log("relay", f"relay {name} -> {'on' if on else 'off'}")
    return f"relay {name} {'on' if on else 'off'}"


@mcp.tool()
def power_mode(mode: str) -> str:
    """Set power policy: eco | normal | max (implemented as an HA input_select + automations)."""
    assert mode in ("eco", "normal", "max")
    _ha("POST", "services/input_select/select_option", entity_id="input_select.nomad_power_mode", option=mode)
    _log("note", f"power mode -> {mode}")
    return f"mode {mode}"


# ---------------------------------------------------------------- radio ----
@mcp.tool()
def radio_get_state() -> dict:
    """IC-705 frequency (Hz), mode, PTT state via rigctld."""
    return {"freq_hz": _rigctl("f"), "mode": _rigctl("m"), "ptt": _rigctl("t")}


@mcp.tool()
def radio_set_freq(mhz: float, mode: str = "FM") -> dict:
    """Tune the IC-705. mode: USB|LSB|FM|AM|CW|PKTUSB."""
    _rigctl(f"F {int(mhz * 1e6)}")
    _rigctl(f"M {mode} 0")
    return radio_get_state()


@mcp.tool()
def radio_ptt(on: bool) -> str:
    """Key/unkey the IC-705. Only use when a skill authorizes transmission."""
    _rigctl(f"T {1 if on else 0}")
    _log("tx", f"PTT {'on' if on else 'off'} {radio_get_state()}")
    return "ptt on" if on else "ptt off"


@mcp.tool()
def radio_send_aprs(text: str) -> str:
    """Send an APRS message/beacon via Direwolf (KISS over TCP :8001). Text <= 67 chars."""
    raise NotImplementedError("Wire to Direwolf KISS (use aprslib/kiss) in Phase 3")


@mcp.tool()
def radio_winlink_send(to: str, subject: str, body: str) -> str:
    """Queue a Winlink email via Pat."""
    subprocess.run(["pat", "compose", "-s", subject, to], input=body.encode(), check=True)
    _log("note", f"winlink queued to {to}: {subject}")
    return "queued; run radio_winlink_sync to transmit"


@mcp.tool()
def radio_winlink_sync(gateway: str = "") -> str:
    """Connect to a Winlink RMS gateway and exchange mail. gateway: Pat alias from config."""
    r = subprocess.run(["pat", "connect", gateway or "default"], capture_output=True, text=True, timeout=900)
    _log("tx", f"winlink sync {gateway or 'default'} rc={r.returncode}")
    return (r.stdout + r.stderr)[-2000:]


# ----------------------------------------------------------------- mesh ----
@mcp.tool()
def mesh_nodes() -> list[dict]:
    """Meshtastic nodes heard: id, name, last heard, SNR, battery, position."""
    import meshtastic.serial_interface  # noqa: PLC0415

    iface = meshtastic.serial_interface.SerialInterface(os.environ.get("MESH_PORT", "/dev/mesh-0"))
    try:
        nodes = []
        for n in (iface.nodes or {}).values():
            u = n.get("user", {})
            nodes.append({
                "id": u.get("id"), "name": u.get("longName"), "short": u.get("shortName"),
                "last_heard": n.get("lastHeard"), "snr": n.get("snr"),
                "battery": n.get("deviceMetrics", {}).get("batteryLevel"),
                "position": n.get("position", {}),
            })
        return nodes
    finally:
        iface.close()


@mcp.tool()
def mesh_send(text: str, to: str | None = None, channel: int = 0) -> str:
    """Send a Meshtastic message (<=200 chars). to=node id for DM, else channel broadcast."""
    import meshtastic.serial_interface  # noqa: PLC0415

    text = text[:200]
    iface = meshtastic.serial_interface.SerialInterface(os.environ.get("MESH_PORT", "/dev/mesh-0"))
    try:
        iface.sendText(text, destinationId=to or "^all", channelIndex=channel, wantAck=True)
        time.sleep(3)
        _log("tx", f"mesh -> {to or 'all'}: {text}")
        return "sent (ack not tracked in skeleton)"
    finally:
        iface.close()


# ------------------------------------------------------------------ sdr ----
@mcp.tool()
def sdr_scan(start_mhz: float, stop_mhz: float, step_khz: float = 12.5, seconds: int = 10) -> list[dict]:
    """Band survey with rtl_power on sdr-0; returns peaks above noise floor as (mhz, dbm)."""
    cmd = ["rtl_power", "-d", "0", "-f", f"{start_mhz}M:{stop_mhz}M:{step_khz}k", "-i", "1", "-e", f"{seconds}s", "-"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=seconds + 30)
    bins: dict[float, float] = {}
    for line in r.stdout.splitlines():
        p = line.split(", ")
        if len(p) < 7:
            continue
        lo, step = float(p[2]), float(p[4])
        for i, v in enumerate(p[6:]):
            f = (lo + i * step) / 1e6
            bins[round(f, 4)] = max(bins.get(f, -200), float(v))
    if not bins:
        return []
    vals = sorted(bins.values())
    floor = vals[len(vals) // 2]
    return sorted(({"mhz": f, "dbm": v} for f, v in bins.items() if v > floor + 10), key=lambda x: -x["dbm"])[:50]


@mcp.tool()
def sdr_monitor_start(freq_mhz: float, mode: str = "fm", minutes: int = 2, keywords: list[str] | None = None) -> str:
    """Record a channel with rtl_fm and transcribe with faster-whisper. Returns a job id."""
    raise NotImplementedError("Phase 2: rtl_fm -> wav -> POST /v1/audio/transcriptions on :9000; publish keyword hits to nomad/alerts")


@mcp.tool()
def sdr_adsb_nearby() -> list[dict]:
    """Aircraft from dump1090's aircraft.json."""
    return httpx.get("http://127.0.0.1:8083/data/aircraft.json", timeout=5).json().get("aircraft", [])


# ------------------------------------------------------------------ gps ----
@mcp.tool()
def gps_fix() -> dict:
    """Current GPS fix from gpsd."""
    import gpsd  # noqa: PLC0415

    gpsd.connect()
    p = gpsd.get_current()
    return {"mode": p.mode, "lat": p.lat, "lon": p.lon, "alt_m": p.alt, "hdop": p.hdop, "time": p.time}


# ------------------------------------------------------------------- kb ----
@mcp.tool()
def kb_search(query: str, book: str | None = None, n: int = 8) -> list[dict]:
    """Search the offline Kiwix library. book is a ZIM name (e.g. wikipedia_en_all_maxi_2026-08)."""
    params = {"pattern": query, "pageLength": n, "format": "xml"}
    if book:
        params["books.name"] = book
    r = httpx.get(f"{KIWIX_URL}/search", params=params, timeout=20)
    r.raise_for_status()
    import xml.etree.ElementTree as ET  # noqa: PLC0415

    root = ET.fromstring(r.text)
    return [
        {"title": i.findtext("title"), "url": KIWIX_URL + (i.findtext("link") or ""), "snippet": i.findtext("description")}
        for i in root.iter("item")
    ]


@mcp.tool()
def kb_read(url: str, max_chars: int = 8000) -> str:
    """Fetch a Kiwix article and return its text (HTML stripped)."""
    import re  # noqa: PLC0415

    html = httpx.get(url, timeout=20).text
    text = re.sub(r"<script.*?</script>|<style.*?</style>", "", html, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text)[:max_chars]


# ------------------------------------------------------------------ net ----
@mcp.tool()
def net_status() -> dict:
    """WAN/LAN health from OpenWrt (ubus over SSH) and inference endpoint checks."""
    out = {}
    try:
        r = subprocess.run(["ssh", "-o", "ConnectTimeout=5", "router", "ubus call mwan3 status"], capture_output=True, text=True, timeout=15)
        out["mwan3"] = json.loads(r.stdout) if r.returncode == 0 else r.stderr
    except Exception as e:  # noqa: BLE001
        out["mwan3"] = f"error: {e}"
    for name, url in {"llama": "http://127.0.0.1:8080/v1/models", "ollama": "http://127.0.0.1:11434/api/tags"}.items():
        try:
            out[name] = httpx.get(url, timeout=5).status_code == 200
        except Exception:  # noqa: BLE001
            out[name] = False
    return out


@mcp.tool()
def comms_check_all(include_sat: bool = False) -> dict:
    """Run the comms self-test (see comms-check skill). Skeleton: composes the other tools."""
    report = {"power": power_status()}
    try:
        report["gps"] = gps_fix()
    except Exception as e:  # noqa: BLE001
        report["gps"] = f"FAIL {e}"
    report["net"] = net_status()
    try:
        report["rig"] = radio_get_state()
    except Exception as e:  # noqa: BLE001
        report["rig"] = f"FAIL {e}"
    _log("check", "comms-check run", **{k: str(v)[:200] for k, v in report.items()})
    return report


if __name__ == "__main__":
    mcp.run()
