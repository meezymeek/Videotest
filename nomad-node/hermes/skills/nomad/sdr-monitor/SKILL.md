---
name: sdr-monitor
description: Use the SDR receivers to scan bands for activity, monitor and transcribe a voice channel with Whisper, decode 433 MHz sensors and ADS-B aircraft, and alert on keywords.
version: 0.1.0
platforms: [linux]
metadata:
  hermes:
    tags: [nomad, sdr, monitoring, whisper]
    category: nomad
    requires_toolsets: [mcp_nomad]
---

# /sdr-monitor

Receive-only. No license needed; no transmit tools used here.

## Tools
- `sdr.scan(start_mhz, stop_mhz, step_khz)` → list of (freq, dBm) peaks above the noise floor.
- `sdr.monitor_start(freq_mhz, mode, minutes, keywords=[])` → job id; records audio and transcribes with faster-whisper; keyword hits are published to `nomad/alerts` immediately.
- `sdr.monitor_result(job_id)` → transcript with timestamps.
- `sdr.decode_433()` → recent rtl_433 sensor packets (weather stations, TPMS, etc.).
- `sdr.adsb_nearby()` → aircraft within range with callsign, altitude, distance.

## Receiver allocation
- `sdr-0` (RTL-SDR): APRS/2 m/70 cm and general monitoring.
- `sdr-1` (RTL-SDR): 433 MHz / ADS-B / weather radio (162.400–162.550 NOAA).
- `sdr-2` (Airspy): HF 0.5–30 MHz via up-converter or direct sampling; band surveys.
Don't start a second job on a receiver that's busy — check `sdr.jobs()` first.

## Typical requests
- "Anything on 146.52?" → 2-minute monitor, report transcript or "no traffic".
- "Weather" → tune `sdr-1` to the strongest NOAA frequency, transcribe 3 minutes, summarize the forecast.
- "What's flying over" → `sdr.adsb_nearby()`.
- "Scan the 2 m band" → `sdr.scan(144, 148, 12.5)` and identify repeaters by offset/tone if known in `references/repeaters.md`.

## Limits
- Whisper on 30 minutes of audio costs ~1–2 minutes of GPU; say so if battery is in eco mode.
- Transcripts are best-effort; always mark uncertain words with [?].
