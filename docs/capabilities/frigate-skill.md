# Frigate v0.17 — AIOS Vision Layer Skill
## Complete reference for IP camera NVR + AI object detection

---

## 1. OVERVIEW

Frigate is a local NVR with AI object detection using OpenCV + TensorFlow Lite.
Runs as Docker container at `aios-frigate:5000` (10.40.0.50, AI zone).
Config bind-mounted: `/aios/configs/frigate/config.yml:/config/config.yml:ro`

**AIOS Context**: Frigate is the vision layer — feeds from IP cameras → GPU object detection → MQTT → n8n workflows → WhatsApp alerts.

### Current Version: 0.17.1-416a9b7 (stable)

---

## 2. CONFIG STRUCTURE (v0.17)

### 2.1 Minimum Valid Config

```yaml
mqtt:
  enabled: true
  host: 10.50.0.20
  port: 1883
  topic_prefix: frigate
  client_id: frigate

cameras:
  camera_name:
    enabled: true
    ffmpeg:
      inputs:
        - path: rtsp://user:pass@ip:554/stream
          roles:
            - detect
    detect:
      width: 1280
      height: 720
      fps: 5

detectors:
  cpu1:
    type: cpu

record:
  enabled: true

snapshots:
  enabled: true

objects:
  track:
    - person
    - car
```

### 2.2 Full Config Structure

```yaml
# ── MQTT ──────────────────────────────────────
mqtt:
  enabled: true
  host: "<host>"
  port: 1883
  topic_prefix: frigate
  client_id: frigate
  user: "<user>"
  password: "<pass>"
  stats_interval: 60
  qos: 0

# ── DETECTORS ────────────────────────────────
detectors:
  cpu1:
    type: cpu
  coral:
    type: edgetpu
    device: usb
  ov:
    type: openvino
    device: AUTO
  trt:
    type: tensorrt

# ── MODEL (for OpenVINO/TensorRT) ────────────
model:
  width: 320
  height: 320
  input_tensor: nhwc
  input_pixel_format: bgr
  path: /openvino-model/ssdlite_mobilenet_v2.xml
  labelmap_path: /openvino-model/coco_91cl_bkgr.txt

# ── FFMPEG ───────────────────────────────────
ffmpeg:
  hwaccel_args: preset-<hardware>
  input_args: preset-rtsp-generic
  output_args:
    detect: preset-record-generic
    record: preset-record-generic

# ── RECORD ───────────────────────────────────
record:
  enabled: true
  motion:
    days: 7
  alerts:
    retain:
      days: 30
      mode: motion
  detections:
    retain:
      days: 30
      mode: motion

# ── SNAPSHOTS ───────────────────────────────
snapshots:
  enabled: true
  timestamp: true
  bounding_box: true
  crop: false
  height: 720
  retain:
    default: 30

# ── OBJECTS ──────────────────────────────────
objects:
  track:
    - person
    - car
    - truck
    - motorcycle
    - bicycle
    - dog
    - cat
  filters:
    person:
      min_score: 0.7
      threshold: 0.8
      mask: poly,0.485,0.113,0.001,0.312,0.001,0.001,0.999,0.001,0.999,0.312

# ── ZONES ────────────────────────────────────
zones:
  driveway:
    coordinates: 0.5,0.5,0.8,0.5,0.8,0.8,0.5,0.8
    objects:
      - person
      - car

# ── BIRDS EYE ───────────────────────────────
birdseye:
  enabled: true
  mode: continuous

# ── GENAI (v0.17+) ──────────────────────────
genai:
  enabled: true
  api_key: sk-...
  provider: openai  # or google
  model: gpt-4o-mini
  object_description:
    enabled: true
    prompt: "Describe the scene briefly"
  review_summary:
    enabled: true
    type: timed  # or default

# ── AUDIO DETECT ────────────────────────────
audio:
  enabled: true
  listen:
    - bark
    - scream
    - speech
    - fire_alarm
  min_volume: 500
  filters:
    bark:
      min_score: 0.7

# ── go2rtc (RESTREAM) ───────────────────────
go2rtc:
  streams:
    camera_name: rtsp://user:pass@ip:554/stream
  webrtc:
    candidates:
      - 10.0.0.100:8555
      - stun:8555
```

---

## 3. CAMERA CONFIGURATION

### 3.1 Camera Entry Structure

```yaml
cameras:
  entrance:
    enabled: true
    ffmpeg:
      inputs:
        - path: rtsp://admin:pass@10.0.0.51:554/cam/realmonitor?channel=1&subtype=0
          roles:
            - detect
            - record
    detect:
      width: 1280    # Detection resolution (usually substream width)
      height: 720
      fps: 5         # Detection framerate (5 is standard, 3 for low-end)
    record:
      enabled: true
    snapshots:
      enabled: true
    motion:
      mask:
        - 0.0,0.0,0.5,0.0,0.5,0.5,0.0,0.5  # Polygon mask coordinates (normalized 0-1)
    zones:
      entrance_door:
        coordinates: 0.4,0.6,0.6,0.6,0.6,0.9,0.4,0.9
    objects:
      track:
        - person
      filters:
        person:
          min_score: 0.8
    onvif:
      host: 10.0.0.51
      port: 8000
      user: admin
      password: pass
    ui:
      order: 1
      dashboard: true
```

### 3.2 Dual-Stream Setup (Best Practice)

Use **substream for detection** (lower res = faster), **main stream for recording** (high res):

```yaml
cameras:
  entrance:
    ffmpeg:
      inputs:
        - path: rtsp://admin:pass@10.0.0.51:554/cam/realmonitor?channel=1&subtype=1
          roles:
            - detect
        - path: rtsp://admin:pass@10.0.0.51:554/cam/realmonitor?channel=1&subtype=0
          roles:
            - record
    detect:
      width: 704      # Substream resolution
      height: 576
      fps: 5
```

### 3.3 Common Camera RTSP URLs

| Brand | Main Stream | Sub Stream |
|-------|-------------|------------|
| Dahua | `rtsp://u:p@ip:554/cam/realmonitor?channel=1&subtype=0` | `...subtype=1` |
| Hikvision | `rtsp://u:p@ip:554/Streaming/Channels/101` | `.../102` |
| Reolink | `rtsp://u:p@ip:554/h264Preview_01_main` | `..._01_sub` |
| Amcrest | `rtsp://u:p@ip:554/cam/realmonitor?channel=1&subtype=0` | `...subtype=1` |
| RTSP (generic) | `rtsp://u:p@ip:554/stream` | `rtsp://u:p@ip:554/substream` |

---

## 4. RECORD RETENTION (v0.17 Format)

Key change in v0.17: `retain` is nested under `alerts` and `detections`, not at top level.

```yaml
record:
  enabled: true
  # Keep all motion-triggered video for 7 days
  motion:
    days: 7
  # Keep alert-classified video (person/car) for 30 days
  alerts:
    retain:
      days: 30
      mode: motion
  # Keep all detection-triggered video for 30 days
  detections:
    retain:
      days: 30
      mode: motion
  # Optional: keep everything for N days
  # everything:
  #   days: 3
```

**Retention modes**: `motion` (keep segments with motion), `active_objects` (keep segments with tracked objects), `all` (keep everything)

---

## 5. DETECTORS

### CPU Detector (default, for testing only)
```yaml
detectors:
  cpu1:
    type: cpu
```
- Uses TensorFlow Lite XNNPACK
- ~5-10ms inference on modern CPU
- **Warning**: "CPU detectors are not recommended and should only be used for testing"

### NVIDIA GPU Detector via TensorRT
```yaml
detectors:
  trt:
    type: tensorrt
    device: 0  # GPU device index
```
- Requires `frigate:latest-tensorrt` Docker tag
- Quadro M4000 (Maxwell CC 5.0) — TensorRT requires CC 5.0+ (M4000 = CC 5.0, supports it)
- Frigate's tensorrt detector requires building a TRT engine first

### Coral EdgeTPU Detector
```yaml
detectors:
  coral:
    type: edgetpu
    device: usb  # or pci
```

---

## 6. HARDWARE ACCELERATION (Video Decoding)

### Presets

| Preset | Hardware | Docker Requires |
|--------|----------|-----------------|
| `preset-nvidia-h264` | NVIDIA GPU (H.264) | `--runtime=nvidia` + `nvidia-container-toolkit` |
| `preset-nvidia-h265` | NVIDIA GPU (H.265) | Same |
| `preset-vaapi` | Intel QuickSync | `/dev/dri` passthrough |
| `preset-intel-qsv-h264` | Intel QSV (H.264) | Same |
| `preset-rpi-64-h264` | Raspberry Pi 64-bit | `/dev/video*` |
| `preset-rpi-64-h265` | Raspberry Pi 64-bit (H.265) | Same |

### Quadro M4000 setup
```yaml
ffmpeg:
  hwaccel_args: preset-nvidia-h264
```
Container has `runtime: nvidia` in docker-compose.
NOTE: Frigate's `frigate:stable` image includes NVIDIA support natively.

---

## 7. go2rtc (Restreaming)

go2rtc runs embedded inside Frigate. It restreams cameras via RTSP/WebRTC to reduce direct camera connections.

```yaml
go2rtc:
  streams:
    entrance:
      - rtsp://admin:pass@10.0.0.51:554/cam/realmonitor?channel=1&subtype=0
    restream_only: ffmpeg:entream#video=h264#hardware  # Reuse frigate's decoded frames
  webrtc:
    candidates:
      - 10.0.0.100:8555
```

Auto-generated go2rtc config picks up camera RTSP paths from ffmpeg inputs.

---

## 8. ZONES

Zones define areas for object filtering. Coordinates are normalized (0.0-1.0) relative to camera frame.

```yaml
zones:
  driveway:
    coordinates: 0.3,0.5, 0.7,0.5, 0.7,0.9, 0.3,0.9
    objects:
      - person
      - car
    # loitering_time: 30  # Alert if object stays in zone > N seconds
  front_door:
    coordinates: 0.0,0.0, 0.4,0.0, 0.4,0.5, 0.0,0.5
    objects:
      - person
```

---

## 9. MASKS

Motion masks prevent false triggers from areas with constant motion (trees, flags, timestamps).

```yaml
motion:
  mask:
    # Single polygon (normalized coordinates)
    - 0.0,0.0, 0.5,0.0, 0.5,0.1, 0.0,0.1
    # Or use object filter mask per object type
objects:
  filters:
    person:
      mask: 0.0,0.0,0.2,0.0,0.2,0.1,0.0,0.1
```

Two types:
- **Motion mask** (`camera.motion.mask`) — ignores motion in that area entirely
- **Object filter mask** (`objects.filters.<label>.mask`) — ignores detections in that area

---

## 10. OBJECT FILTERS

```yaml
objects:
  track:
    - person
    - car
  filters:
    person:
      min_score: 0.7        # Minimum detection score to consider
      threshold: 0.85       # Minimum score for stationary object
      max_ratio: 0.8        # Max ratio of bounding box (w/h)
      min_area: 5000        # Min bounding box area in pixels
      max_area: 100000      # Max bounding box area in pixels
      mask: poly,...         # Area polygon to ignore detections
    car:
      min_score: 0.6
      min_area: 10000
    dog:
      min_score: 0.8
      threshold: 0.9
```

---

## 11. GENAI ENRICHMENTS (v0.17+)

```yaml
genai:
  enabled: true
  provider: openai   # openai or google
  api_key: sk-...
  model: gpt-4o-mini  # or gemini-1.5-flash for google
  object_description:
    enabled: true
    prompt: "Describe what the person is wearing and carrying"
  review_summary:
    enabled: true
    type: timed   # Summarize at set intervals
    interval: 60 # seconds
```

### AIOS Note
GenAI requires Bifrost routing. Configure:
```yaml
genai:
  api_key: sk-aios-bifrost  # Virtual key
  # Frigate calls OpenRouter-compatible endpoint
  # Custom endpoint not natively supported — use reverse proxy or direct OpenRouter
```

---

## 12. AUDIO DETECTION

```yaml
audio:
  enabled: true
  listen:
    - bark
    - scream
    - speech
    - fire_alarm
    - glass_break
  min_volume: 500
  filters:
    scream:
      min_score: 0.7
```

---

## 13. MQTT INTEGRATION

Frigate publishes events to MQTT topics:

```
frigate/events                   — All detection events (JSON)
frigate/<camera>/<object>/snapshot — Snapshot images
frigate/available                — "online" / "offline"
frigate/stats                    — System stats
```

Publish to control:
```
frigate/<camera>/snapshot        — Request snapshot (POST empty)
```

### AIOS Pipeline
```
Frigate detects person → MQTT (10.50.0.20:1883)
  → n8n surveillance workflow → Bifrost/LLM evaluates
  → WhatsApp/Telegram alert to client
```

---

## 14. HTTP API (Key Endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/version` | Frigate version |
| GET | `/api/stats` | System stats + camera stats |
| GET | `/api/config` | Current config |
| GET | `/api/config/schema.json` | JSON Schema for validation |
| GET | `/api/events` | List events (query: `?camera=entrance&label=person`) |
| GET | `/api/events/<id>/snapshot.jpg` | Event snapshot |
| GET | `/api/events/<id>/clip.mp4` | Event clip |
| DELETE | `/api/events/<id>` | Delete event |
| POST | `/api/events/<id>/retain` | Retain event |
| GET | `/api/<camera>/latest.jpg` | Latest snapshot |
| GET | `/api/<camera>/<start>/<end>/clip.mp4` | Clip by timestamp |
| POST | `/api/recordings/<camera>/<path>` | Delete recording |
| GET | `/api/review` | Review items (query: `?before=ts&after=ts&cameras=entrance`) |
| GET | `/api/export` | List exports |
| POST | `/api/export/<id>/cancel` | Cancel export |
| GET | `/api/logs/<service>` | Logs (frigate, go2rtc, nginx) |
| GET | `/api/preview/<camera>/start/<ts>/end/<ts>` | Preview thumbnails |
| POST | `/api/retain/<id>` | Retain an event |
| GET | `/api/faces` | Face recognition (if configured) |
| GET | `/api/license_plates` | LPR (if configured) |
| GET | `/api/birdseye` | Birdseye settings |
| POST | `/api/snapshot/<camera>` | Request manual snapshot |
| POST | `/api/recordings/<camera>/retain` | Retain recordings |

---

## 15. FRIGATE+ (Premium Subscriptions)

Paid service for improved detection models:
- Submit annotated images → custom model trained for your cameras
- Better accuracy on specific scenes
- `https://frigate.video/plus/`

---

## 16. SEMANTIC SEARCH (v0.17+)

```yaml
semantic_search:
  enabled: true
  model: intel/dynamic_tinybert  # Local model
  reindex: false   # Set true to re-index existing events
```

Search events by natural language: "person carrying package near front door"
Uses local sentence-transformers model.

---

## 17. FACE RECOGNITION

```yaml
face_recognition:
  enabled: true
  model: facenet  # Local model
  min_score: 0.8
```

Requires known face embeddings to be loaded. Faces tracked across events.

---

## 18. AIOS-SPECIFIC CONFIGURATION

### Docker Compose (current)
```yaml
frigate:
  image: ghcr.io/blakeblackshear/frigate:stable
  container_name: aios-frigate
  runtime: nvidia  # GPU access
  ports:
    - "5000:5000"
  volumes:
    - /aios/configs/frigate/config.yml:/config/config.yml:ro
    - frigate-data:/media/frigate
    - /dev/bus/usb:/dev/bus/usb  # For USB Coral (future)
  environment:
    - FRIGATE_RTSP_PASSWORD=${EXT_2000_SECRET}
  networks:
    aios-ai:
      ipv4_address: 10.40.0.50
    aios-voice:
    aios-mon:
```

### SHM Size Warning
```
Current SHM size of 64.0MB is too small, recommend increasing it to at least 114MB.
```
Fix in compose:
```yaml
frigate:
  shm_size: "128mb"  # Add this to service
```

### GPU Detector Setup (Quadro M4000)
The Quadro M4000 (Maxwell CC 5.0) uses NVIDIA driver 470 + CUDA 11.4.
- CPU detector works but is slow
- TensorRT detector requires `frigate:latest-tensorrt` image
- For now: **CPU detector is fine for 1-2 cameras at 5fps**

---

## 19. TROUBLESHOOTING

### Safe Mode
Frigate enters safe mode on config validation errors — recording/events disabled.
Check logs: `docker logs aios-frigate | grep -A 10 "Config Validation"`

### Common Config Errors (v0.17)

| Error | Cause | Fix |
|-------|-------|-----|
| `record -> retain - Extra inputs` | Old `retain: {days, mode}` format | Use `motion.days`, `alerts.retain`, `detections.retain` |
| `cameras - Field required` | Missing `cameras:` key | Add at least one camera |
| `cameras - Value: None` | Empty `cameras:` section | Add a placeholder camera or real entry |
| `genai -> enabled - Extra inputs` | `genai:` not supported in this version | Add or remove genai section (v0.17 supports it) |
| `Did not detect hwaccel` | HW acceleration not available | Check NVIDIA drivers or fall back to CPU |

### High CPU Usage
- Reduce detection FPS: `detect.fps: 3` instead of 5
- Use substream for detection (lower resolution)
- Add motion masks for areas with constant motion
- Decrease detection width/height

---

## 20. QUICK COMMANDS

```bash
# Restart frigate
docker restart aios-frigate

# Check config validation
docker logs aios-frigate | grep -E "Config|Error|WARN"

# View detected objects
curl -s http://10.0.0.100:5000/api/events?limit=10 | jq .[]

# Check camera stats
curl -s http://10.0.0.100:5000/api/stats | jq .cameras

# Test RTSP stream from server
ffmpeg -rtsp_transport tcp -i "rtsp://user:pass@camera:554/stream" -t 3 -f null -

# Get MQTT events
mosquitto_sub -h 10.50.0.20 -t "frigate/#" -v

# Apply config change (edit locally, scp, restart)
scp config.yml ai@10.0.0.100:/aios/configs/frigate/config.yml
ssh ai@10.0.0.100 "docker restart aios-frigate"
```

---

## 21. AIOS VISION PIPELINE

```
IP Camera (10.0.0.51)
  → RTSP → Frigate (10.40.0.50:5000)
    → GPU YOLO object detection (person, car, dog, etc.)
    → MQTT event (10.50.0.20:1883) → frigate/events
    → n8n surveillance workflow (10.20.0.10:5678)
      → Bifrost LLM evaluation (10.40.0.10:4000)
      → WhatsApp/Telegram alert to client
    → Recordings stored in frigate-data volume (7 day retention)
    → Snapshots stored for review (30 day retention)
    → Frigate UI for live view + event review
```

---

*Compiled June 19, 2026 from docs.frigate.video for AIOS Vision Layer*
*Frigate v0.17.1-416a9b7 · Quadro M4000 · GPU AI Zone 10.40.0.50*
