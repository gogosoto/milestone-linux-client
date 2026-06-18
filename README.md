# Milestone Smart Client for Linux

Native Linux client for Milestone XProtect VMS with **full Smart Client feature parity**.

Three-protocol architecture + optional Windows bridge for .NET-only features.

## Architecture

```
Linux Client (PySide6 + aiortc)
  ├── REST (API Gateway)        →  Config, Alarms, Events, Bookmarks, WebRTC
  ├── WebRTC (aiortc)           →  Live/Playback video, audio, PTZ
  ├── Mobile XML-RPC            →  Camera tree, sequences, carousel, thumbnails,
  │                                  two-way audio, export, multi-camera playback
  └── gRPC Bridge ──→ Windows   →  Smart Search, Evidence Lock, Privacy Masking,
                      (.NET 8)      Video Walls, HW Discovery, System Logs
```

## Quick Start

### 1. Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Compile gRPC stubs (for bridge support)

```bash
python -m grpc_tools.protoc \
  -I proto \
  --python_out=src/protocols/bridge \
  --grpc_python_out=src/protocols/bridge \
  proto/bridge.proto
```

### 3. Configure

Create `~/.config/milestone-client/config.yaml`:

```yaml
servers:
  - name: production
    server_url: https://vms-server.example.com
    api_gateway_url: https://vms-server.example.com/api
    username: admin
    auth_type: basic
    bridge_host: vms-server.example.com
    bridge_port: 50051
active_server: production
```

### 4. Run

```bash
python -m src.main
```

### 5. (Optional) Deploy Windows Bridge

On your Windows Recording Server:

```powershell
cd bridge/MilestoneBridge
dotnet restore
dotnet run --urls http://0.0.0.0:50051
```

## Protocol Coverage

| Feature | Protocol | Status |
|---------|----------|--------|
| **Live video** | WebRTC (aiortc) | ✅ |
| **Playback + timeline** | WebRTC (playbackTime) | ✅ |
| **Audio** | WebRTC + Mobile XML-RPC | ✅ |
| **Two-way audio / PTT** | Mobile XML-RPC | ✅ |
| **PTZ control** | WebRTC data channel | ✅ |
| **PTZ presets** | Mobile XML-RPC | ✅ |
| **PTZ tours/patrols** | gRPC Bridge | ⏳ |
| **Camera tree** | Mobile XML-RPC | ✅ |
| **Multi-view grid** | N WebRTC sessions | ✅ |
| **Sequences / tours** | Mobile XML-RPC | ✅ |
| **Carousel mode** | Mobile XML-RPC | ✅ |
| **Thumbnails** | Mobile XML-RPC | ✅ |
| **Export / investigations** | Mobile XML-RPC | ✅ |
| **Alarms** | REST | ✅ |
| **Bookmarks** | REST | ✅ |
| **User-defined events** | REST | ✅ |
| **Event subscription** | WebSocket | ✅ |
| **ONVIF discovery** | WS-Discovery + onvif-zeep | ✅ |
| **Smart Search** | gRPC Bridge | ⏳ |
| **Evidence Lock** | gRPC Bridge | ⏳ |
| **Privacy Masking** | gRPC Bridge | ⏳ |
| **Video Wall / Matrix** | gRPC Bridge | ⏳ |
| **Hardware management** | gRPC Bridge | ⏳ |
| **System logs / status** | gRPC Bridge | ⏳ |
| **GIS / Maps** | Custom (QtWebEngine + Leaflet) | 🚧 |

## Project Structure

```
src/
├── main.py                         # Entry point
├── core/                           # Config, auth, session, event bus
├── ui/                             # Qt6 widgets (PySide6)
│   ├── main_window.py              # Multi-view grid + docking
│   ├── camera_view_widget.py       # WebRTC video renderer
│   ├── ptz_control_panel.py        # PTZ joystick + presets
│   ├── alarm_panel.py              # Alarm list
│   ├── playback_timeline.py        # Timeline controls
│   └── settings_dialog.py          # Connection setup
├── protocols/                      # Protocol adapters
│   ├── rest_api/                   # API Gateway REST
│   ├── mobile_xmlrpc/              # XProtect Mobile XML-RPC
│   ├── webrtc/                     # aiortc WebRTC pipeline
│   ├── websocket_events/           # Event & State WS
│   ├── onvif/                      # WS-Discovery + device info
│   └── bridge/                     # gRPC → Windows .NET shim
├── models/                         # Domain models
└── services/                       # Business logic
bridge/                             # Windows .NET Bridge
proto/                              # Shared gRPC protobuf
```

## Development

```bash
# Install with dev deps
pip install -e ".[dev]"

# Run tests
pytest

# Watch
find . -name '*.py' | entr -c python -m src.main
```
