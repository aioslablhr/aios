# Dahua IP Camera — AIOS Vision Layer Skill
## Complete reference for Dahua camera integration with Frigate NVR

---

## 1. CAMERA MODELS IN AIOS

### Current Camera: DH-IPC-B1E49-A-IL (ECO Series)
```
Location:    10.0.0.51 (LAN)
Type:        4MP Smart Dual Light Fixed-focal Bullet
Status:      Active — RTSP streaming to Frigate
```

### Specs
| Property | Value |
|----------|-------|
| Sensor | 1/3" CMOS, 4MP (2560×1440) |
| Max FPS | 30fps @ 4MP |
| Codec | H.265, H.264, Smart H.265+, Smart H.264+ |
| Night Vision | Smart Dual Light — IR 30m, Warm Light 15m |
| Audio | Built-in mic |
| Detection | On-device human detection (AI) |
| Power | 12VDC / PoE (IEEE 802.3af) |
| Protection | IP67 (dust + 1m water 30min) |
| Material | Plastic |
| Dimensions | 198.9×80.2×76.2mm |
| Weight | 0.25kg |
| ONVIF | Yes (Profile S, Profile G) |
| Web UI | HTTP on port 80 (Digest auth) |

---

## 2. NETWORK PORTS

| Port | Protocol | Service | Purpose |
|------|----------|---------|---------|
| 80 | TCP | HTTP | Web admin interface (Digest auth login) |
| 554 | TCP | RTSP | Video streaming |
| 37777 | TCP | Dahua SDK | Proprietary push/event API |
| 1900 | UDP | UPnP | Device discovery |
| 5000 | TCP | ONVIF | ONVIF device discovery |

---

## 3. RTSP STREAM URLS

### Dahua Format
```
Main stream:   rtsp://user:pass@ip:554/cam/realmonitor?channel=1&subtype=0
Sub stream:    rtsp://user:pass@ip:554/cam/realmonitor?channel=1&subtype=1
```

### B1E49-A-IL Stream Details
| Stream | Resolution | Codec | FPS | Bitrate |
|--------|-----------|-------|-----|---------|
| Main (subtype=0) | 2560×1440 | H.265 | 25 | ~2-4 Mbps |
| Sub (subtype=1) | 704×576 (D1) | H.265 | 10 | ~256-512 Kbps |

### URL Encoding
Special characters in passwords must be URL-encoded:
```
*  →  %2A
@  →  %40
#  →  %23
$  →  %24
%  →  %25
space → %20
```

Current camera auth: `rtsp://admin:Lahore999!@10.0.0.51:554/...`

---

## 4. WEB ADMIN INTERFACE

- URL: `http://10.0.0.51/` (or `http://admin:Lahore999!@10.0.0.51/`)
- Auth: Digest authentication (NOT Basic)
- Default ports: HTTP 80, HTTPS 443 (if enabled)

### Default Credentials
| User | Password | Notes |
|------|----------|-------|
| admin | Lahore999! | Current — changed from Lahore*999 (Digest auth bug) |

### CGI API Endpoints
```
GET /cgi-bin/magicBox.cgi?action=getSystemInfo         → System info
GET /cgi-bin/magicBox.cgi?action=getSoftwareVersion    → Firmware version
GET /cgi-bin/configManager.cgi?action=getConfig&name=Network → Network config
GET /cgi-bin/configManager.cgi?action=getConfig&name=Video  → Video config
POST /cgi-bin/configManager.cgi?action=setConfig&name=Video  → Set video config
```

---

## 5. FRIGATE INTEGRATION

### Recommended Dual-Stream Config

```yaml
cameras:
  entrance:
    enabled: true
    ffmpeg:
      inputs:
        # Substream for detection (D1/704x576 — fast)
        - path: rtsp://admin:Lahore999!@10.0.0.51:554/cam/realmonitor?channel=1&subtype=1
          roles:
            - detect
        # Main stream for recording (4K/2560x1440 — high quality)
        - path: rtsp://admin:Lahore999!@10.0.0.51:554/cam/realmonitor?channel=1&subtype=0
          roles:
            - record
    detect:
      width: 704
      height: 576
      fps: 5
    objects:
      track:
        - person
        - car
    zones:
      driveway:
        coordinates: 0.3,0.5,0.7,0.5,0.7,0.9,0.3,0.9
        objects:
          - person
          - car
```

### Why Substream for Detection
- 704×576 is ~6x fewer pixels than 2560×1440
- Frigate processes detection frames faster at lower resolution
- Main stream saved for recording — full quality when reviewing events
- Detection at 5fps is sufficient for person/car tracking

### go2rtc Restream
```yaml
go2rtc:
  streams:
    entrance:
      - rtsp://admin:Lahore999!@10.0.0.51:554/cam/realmonitor?channel=1&subtype=0
    entrance_sub:
      - rtsp://admin:Lahore999!@10.0.0.51:554/cam/realmonitor?channel=1&subtype=1
```

---

## 6. ONVIF CONFIGURATION

ONVIF allows Frigate to PTZ control, get camera info, and detect motion.

```yaml
cameras:
  entrance:
    onvif:
      host: 10.0.0.51
      port: 8000    # Default ONVIF port for Dahua
      user: admin
      password: "Lahore999!"
    # Autotracking (if PTZ camera):
    # autotracking:
    #   enabled: true
```

---

## 7. CAMERA HARDWARE FEATURES

### Smart Dual Light
- Default: IR LEDs at night (invisible, 30m range)
- On human detection: switches to warm white light (15m)
- Captures full-color video during events
- Returns to IR when person leaves
- **Configurable via web UI**: Setup → Camera → Illumination

### Human Detection (On-Device AI)
- Camera has built-in AI for human detection
- Reduces false alarms from animals/leaves/cars
- Can be configured to trigger alarms/email/SD recording
- **For Frigate**: Disable camera's own motion alerts — let Frigate handle detection

### Built-in Mic
- Camera has internal microphone
- Audio stream available via RTSP (if enabled in stream config)
- Frigate v0.17 supports audio detection (bark, scream, speech, fire_alarm)

```
cameras:
  entrance:
    audio:
      enabled: true
      listen:
        - scream
        - glass_break
```

---

## 8. DAHUA CGI COMMANDS (Useful for Automation)

### Get/Set Config
```bash
# Get all config
curl -u admin:Lahore999! "http://10.0.0.51/cgi-bin/configManager.cgi?action=getConfig&name=All"

# Get video settings
curl -u admin:Lahore999! "http://10.0.0.51/cgi-bin/configManager.cgi?action=getConfig&name=Video"

# Get network settings
curl -u admin:Lahore999! "http://10.0.0.51/cgi-bin/configManager.cgi?action=getConfig&name=Network"

# Set bitrate (main stream)
curl -u admin:Lahore999! -X POST "http://10.0.0.51/cgi-bin/configManager.cgi?action=setConfig&Video.MainFormat.0.BitRate=4096"

# Reboot camera
curl -u admin:Lahore999! "http://10.0.0.51/cgi-bin/magicBox.cgi?action=reboot"

# Get system info
curl -u admin:Lahore999! "http://10.0.0.51/cgi-bin/magicBox.cgi?action=getSystemInfo"
```

### Snapshot via CGI
```bash
curl -u admin:Lahore999! "http://10.0.0.51/cgi-bin/snapshot.cgi" -o snapshot.jpg
```

---

## 9. DAHUA RTSP OVER TCP VS UDP

| Transport | Pros | Cons |
|-----------|------|------|
| UDP | Lower latency | Packet loss in poor networks |
| TCP | Reliable, no packet loss | Slightly higher latency |

Frigate defaults to TCP for RTSP. Configured via:
```yaml
ffmpeg:
  input_args: preset-rtsp-generic   # TCP by default
```

For Dahua, TCP is recommended (more stable across PoE switches).

---

## 10. FIRMWARE & MAINTENANCE

- Web UI: `http://10.0.0.51/` → Settings → System → Update
- Current firmware: Unknown (check via `getSoftwareVersion` CGI)
- Dahua support: `https://www.dahuasecurity.com/support`

### Factory Reset
1. Physical button: Press and hold reset button (inside SD card slot) for 10s
2. Via web: Settings → System → Default → Factory Default
3. Via CGI: `POST /cgi-bin/magicBox.cgi?action=reset`

Factory default IP: 192.168.1.108 (DHCP enabled)

---

## 11. AIOS VISION PIPELINE (Camera → Frigate → n8n)

```
IP Camera (10.0.0.51)
  → RTSP (substream) → Frigate detect (10.40.0.50:5000)
    → GPU/CPU processes frames → object detection (person/car)
    → Event published to MQTT (10.50.0.20:1883)
      → frigate/events — JSON with label, score, bounding box, snapshot
      → n8n surveillance workflow subscribes via MQTT node
        → Bifrost/LLM evaluates event severity (10.40.0.10:4000)
        → WhatsApp/Telegram alert to client
    → Recordings stored in frigate-data volume (main stream)
    → Snapshots for review UI (Frigate web interface)
  → On-site: Camera's own SD card recording (fallback/backup)
```

---

## 12. COMPARISON: DAHUA B1E49-A-IL vs OTHER MODELS

| Feature | B1E49-A-IL (ECO) | HFW1430DS-SAW (WiFi) | N53AB52 (Starlight) |
|---------|-------------------|---------------------|---------------------|
| Resolution | 4MP (2560×1440) | 4MP (2560×1440) | 5MP (2592×1944) |
| Night Vision | Dual Light (IR+Warm) | IR only | Starlight (low-light) |
| AI Detection | Human | — | — |
| WiFi | — | 2.4GHz 802.11b/g/n | — |
| Mic | Built-in | Built-in | — |
| Price Tier | Budget | Budget | Mid-range |

---

## 13. COMMON DAHUA ISSUES & FIXES

| Issue | Cause | Fix |
|-------|-------|-----|
| RTSP auth failure | Special chars in password | URL-encode the password (`*` → `%2A`) |
| Web UI 401 | Digest auth required | Use browser (handles Digest), NOT curl without `--digest` |
| Camera not accessible | DHCP IP changed | Check router DHCP leases, use static IP |
| Poor night vision | IR blocked / dirty lens | Clean lens; ensure no obstructions |
| Frigate can't connect | Camera on different VLAN | Ensure 10.0.0.0/24 routing from Docker AI zone |
| Stream drops | PoE power insufficient | Use proper PoE switch or 12VDC adapter |

---

## 14. QUICK COMMANDS

```bash
# Test RTSP stream (from server)
ffmpeg -rtsp_transport tcp -i "rtsp://admin:Lahore999!@10.0.0.51:554/cam/realmonitor?channel=1&subtype=0" -t 3 -f null -

# Get snapshot
curl -u "admin:Lahore999!" --digest "http://10.0.0.51/cgi-bin/snapshot.cgi" -o cam_snapshot.jpg

# Get system info
curl -u "admin:Lahore999!" --digest "http://10.0.0.51/cgi-bin/magicBox.cgi?action=getSystemInfo"

# Reboot camera
curl -u "admin:Lahore999!" --digest "http://10.0.0.51/cgi-bin/magicBox.cgi?action=reboot" -X POST

# Get Frigate event for this camera
curl -s "http://10.0.0.100:5000/api/events?camera=entrance&limit=5" | jq .

# Check camera is streaming in Frigate
curl -s "http://10.0.0.100:5000/api/stats" | jq .cameras.entrance
```

---

## 15. ACCESSORIES

| Model | Type | Purpose |
|-------|------|---------|
| DH-PFA130-E | Junction Box | Waterproof cable connection |
| DH-PFA151 | Corner Mount Bracket | Corner installation |
| DH-PFA152-E | Pole Mount Bracket | Pole installation |
| DH-PFA134 | Junction Box | Standard junction box |
| DH-PFM321-EN | Power Adapter | DC12V 1A |
| G3416GW | Water Joint | G3/4" weatherproof connector |

---

*Compiled June 19, 2026 for AIOS Vision Layer*
*Camera: DH-IPC-B1E49-A-IL · 10.0.0.51 · Frigate v0.17.1*
