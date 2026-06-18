# Milestone Smart Client for Linux

Native Linux desktop client for Milestone XProtect VMS with **full Smart Client feature parity**.

## Architecture

```
Linux Desktop (PySide6 + aiortc)
  ├── REST API Gateway     →  Config, Alarms, Events, Bookmarks, WebRTC session mgmt
  ├── WebRTC (aiortc)      →  Live/playback video, audio, PTZ data channel
  └── gRPC Bridge ──→ Windows (.NET 8)
       (Recording Server)     VideoOS.Platform.SDK
                              ├── Smart Search / Motion Search
                              ├── Evidence Lock
                              ├── Privacy Masking / Restricted Media
                              ├── Hardware Discovery (ONVIF via server)
                              ├── Hardware Management (add/remove/firmware)
                              ├── Video Wall / Matrix control
                              ├── System Logs / Status
                              └── PTZ Tours / Patrols
```

The Windows bridge is optional — it only provides features that exist exclusively in the .NET SDK. Everything else works directly from Linux.

## Quick Start

```bash
pip install -r requirements.txt
python -m src.main
```

File > Connect → enter your server URL and credentials → double-click a camera in the tree.

## Protocol Coverage

| Feature | Protocol | Status |
|---------|----------|--------|
| **Live video** | WebRTC (aiortc) | ✅ |
| **Playback + timeline** | WebRTC (playbackTime) | ✅ |
| **Audio** | WebRTC | ✅ |
| **Two-way audio** | WebRTC | 🚧 |
| **PTZ control** | WebRTC data channel | ✅ |
| **Camera tree** | REST Config API | ✅ |
| **Multi-view grid** | N x WebRTC sessions | ✅ |
| **Alarms** | REST | ✅ |
| **Bookmarks** | REST | ✅ |
| **Events** | REST + WebSocket | 🚧 |
| **Sequences / tours** | Client-side UI cycling | 🚧 |
| **ONVIF discovery** | WS-Discovery (direct from Linux) | ✅ |
| **Smart Search** | gRPC Bridge | ⏳ |
| **Evidence Lock** | gRPC Bridge | ⏳ |
| **Privacy Masking** | gRPC Bridge | ⏳ |
| **Video Wall** | gRPC Bridge | ⏳ |
| **Hardware Mgmt** | gRPC Bridge | ⏳ |
| **System Status** | gRPC Bridge | ⏳ |
| **Maps / GIS** | QtWebEngine + Leaflet | 🚧 |

## Project Structure

```
src/
├── main.py                     # Entry point (qasync Qt + asyncio)
├── core/                       # Config, OAuth2 auth, session, event bus
├── ui/                         # PySide6 widgets
│   ├── main_window.py          # Multi-view grid + docking
│   ├── camera_view_widget.py   # WebRTC → QImage rendering
│   ├── ptz_control_panel.py    # PTZ joystick + presets
│   ├── alarm_panel.py          # Alarm table
│   ├── playback_timeline.py    # Timeline slider + speed
│   └── settings_dialog.py      # Server connection setup
├── protocols/
│   ├── rest_api/               # API Gateway: Config, Alarms, Events, Bookmarks, WebRTC
│   ├── webrtc/                 # aiortc pipeline + session manager
│   ├── websocket_events/       # Event & State WebSocket subscription
│   ├── onvif/                  # WS-Discovery camera discovery
│   └── bridge/                 # gRPC → Windows .NET shim
├── models/                     # Domain models
└── services/                   # Business logic layer

bridge/                         # Windows .NET 8 gRPC server
proto/                          # Shared protobuf definitions
```

## Windows Bridge (for .NET-only features)

Deploy on your Windows Recording Server:

```powershell
dotnet run --project bridge/MilestoneBridge --urls http://0.0.0.0:50051
```

Configure the bridge host in File > Connect. The Linux client calls the bridge transparently for Smart Search, hardware management, evidence lock, and system status.
