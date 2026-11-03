"""Meshtastic <-> MQTT <-> Hermes bridge.

- Every received mesh packet is published to MQTT `nomad/mesh/rx` (Home Assistant sees it).
- A DM addressed to this node is forwarded to the Hermes API server; the reply goes back
  to the sender over the mesh, chunked to 200 chars.

Hermes API Server (verified): POST http://127.0.0.1:8642/v1/chat/completions, bearer API_SERVER_KEY.
Enable with API_SERVER_ENABLED=true in ~/.hermes/.env.

Deps: pip install meshtastic paho-mqtt httpx pypubsub
"""

from __future__ import annotations

import json
import os
import time

import httpx
import meshtastic.serial_interface
import paho.mqtt.client as mqtt
from pubsub import pub

MESH_PORT = os.environ.get("MESH_PORT", "/dev/mesh-0")
MQTT_HOST = os.environ.get("MQTT_HOST", "127.0.0.1")
HERMES_API = os.environ.get("HERMES_API", "http://127.0.0.1:8642/v1/chat/completions")
HERMES_KEY = os.environ.get("HERMES_API_KEY", "")
MAX_CHUNK = 200

mq = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mq.connect(MQTT_HOST, 1883, 60)
mq.loop_start()

iface = meshtastic.serial_interface.SerialInterface(MESH_PORT)
MY_ID = iface.myInfo.my_node_num


def ask_hermes(sender: str, text: str) -> str:
    body = {
        "model": "hermes",
        "messages": [
            {"role": "system", "content": "Channel: meshtastic. Reply in <= 200 characters, plain text, no markdown."},
            {"role": "user", "content": f"[from {sender}] {text}"},
        ],
        "user": sender,
    }
    headers = {"Authorization": f"Bearer {HERMES_KEY}"} if HERMES_KEY else {}
    r = httpx.post(HERMES_API, json=body, headers=headers, timeout=180)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"].strip()


def send_chunks(dest: int, text: str) -> None:
    for i in range(0, len(text), MAX_CHUNK):
        iface.sendText(text[i : i + MAX_CHUNK], destinationId=dest, wantAck=True)
        time.sleep(2)


def on_receive(packet, interface):  # noqa: ANN001
    try:
        decoded = packet.get("decoded", {})
        mq.publish("nomad/mesh/rx", json.dumps({
            "from": packet.get("fromId"), "to": packet.get("toId"),
            "portnum": decoded.get("portnum"), "text": decoded.get("text"),
            "rx_time": packet.get("rxTime"), "snr": packet.get("rxSnr"),
        }))
        if decoded.get("portnum") != "TEXT_MESSAGE_APP":
            return
        if packet.get("to") != MY_ID:
            return
        text = decoded.get("text", "")
        sender = packet.get("fromId", "unknown")
        if any(k in text.lower() for k in ("mayday", "emergency", "sos", "medical")):
            mq.publish("nomad/alerts", json.dumps({"source": "mesh", "from": sender, "text": text}))
        reply = ask_hermes(sender, text)
        send_chunks(packet["from"], reply)
    except Exception as e:  # noqa: BLE001
        print("bridge error:", e)


pub.subscribe(on_receive, "meshtastic.receive")

print(f"meshtastic bridge up on {MESH_PORT}, node {MY_ID:#x}")
while True:
    time.sleep(60)
