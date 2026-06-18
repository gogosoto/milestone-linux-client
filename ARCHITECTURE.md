# Milestone Linux Smart Client — Full Architecture

## Tech Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| **Language** | Python 3.11+ | Maximum vibe velocity. Everything we need has bindings. |
| **GUI** | PySide6 (Qt6) | Stable, native look, good perf, QtWebEngine for embedded browser if needed |
| **Video** | aiortc (Python-native WebRTC) | No GStreamer complexity. `pip install aiortc`. Async-native. |
| **REST** | httpx (async) | Native async, HTTP/2, works great with asyncio |
| **Mobile Protocol** | Python + asyncio | Custom XML-RPC over httpx — straightforward |
| **WebSocket** | websockets | For Event & State WS API |
| **ONVIF** | onvif-zeep | Standard ONVIF camera discovery/control |
| **gRPC** | grpcio | Bridge to Windows .NET shim |
| **Windows Bridge** | .NET 8 + gRPC + VideoOS.Platform.SDK | 500-line shim, runs on existing Windows Recording Server |

---

## Project Structure

```
milestone-linux-client/
├── README.md
├── pyproject.toml
├── requirements.txt
│
├── src/
│   ├── __init__.py
│   ├── main.py                          # Entry point
│   │
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── app.py                       # PySide6 QApplication setup
│   │   ├── main_window.py               # Main window (multi-view grid)
│   │   ├── camera_view_widget.py        # Single camera view (video + overlay)
│   │   ├── camera_tree.py               # Left panel camera tree
│   │   ├── alarm_panel.py               # Alarm list panel
│   │   ├── playback_timeline.py         # Playback slider + controls
│   │   ├── ptz_control_panel.py         # PTZ joystick + presets
│   │   ├── export_dialog.py             # Export wizard
│   │   ├── map_widget.py                # GIS/Leaflet map (QtWebEngine)
│   │   ├── settings_dialog.py           # Server connection settings
│   │   └── thumbnails.py               # Thumbnail grid widget
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── auth.py                      # OAuth2 token management
│   │   ├── session.py                   # Connection state, multi-server
│   │   ├── config.py                    # User config (servers, credentials)
│   │   └── event_bus.py                # In-app signal bus (PySide signals)
│   │
│   ├── protocols/
│   │   ├── __init__.py
│   │   ├── rest_api/                    # API Gateway REST
│   │   │   ├── __init__.py
│   │   │   ├── client.py                # Base REST client (auth, retry)
│   │   │   ├── alarms.py                # Alarms CRUD
│   │   │   ├── events.py               # Events CRUD
│   │   │   ├── config.py               # Config CRUD (cameras, users, etc.)
│   │   │   ├── bookmarks.py            # Bookmarks CRUD
│   │   │   └── webrtc.py               # WebRTC session init (REST side)
│   │   │
│   │   ├── mobile_xmlrpc/               # XProtectMobile XML-RPC protocol
│   │   │   ├── __init__.py
│   │   │   ├── client.py                # HTTP transport + DH auth + CHAP
│   │   │   ├── auth.py                  # Diffie-Hellman + CHAP implementation
│   │   │   ├── commands.py              # All command builders
│   │   │   ├── parser.py                # XML response parser
│   │   │   ├── connection.py            # Connection lifecycle
│   │   │   ├── views.py                 # Camera tree, views
│   │   │   ├── video.py                 # Stream request/change/close
│   │   │   ├── sequences.py            # Tours/sequences
│   │   │   ├── carousel.py             # Carousel commands
│   │   │   ├── thumbnails.py           # GetThumbnailByTime
│   │   │   ├── export.py               # Export/investigations
│   │   │   ├── audio.py                # Two-way audio push
│   │   │   └── playback.py             # CreatePlaybackController
│   │   │
│   │   ├── webrtc/                      # WebRTC media pipeline
│   │   │   ├── __init__.py
│   │   │   ├── client.py                # aiortc RTCPeerConnection wrapper
│   │   │   ├── video_renderer.py        # Frame → QImage → QWidget
│   │   │   ├── audio_handler.py         # Audio playback/capture
│   │   │   ├── ptz_channel.py           # WebRTC data channel (PTZ commands)
│   │   │   └── session_manager.py       # Manage N concurrent WebRTC sessions
│   │   │
│   │   ├── websocket_events/            # Event & State WS API
│   │   │   ├── __init__.py
│   │   │   ├── client.py                # WebSocket connection
│   │   │   └── handlers.py             # Event → UI dispatch
│   │   │
│   │   ├── onvif/                       # Camera discovery
│   │   │   ├── __init__.py
│   │   │   ├── discovery.py             # WS-Discovery multicast probe
│   │   │   ├── device.py               # ONVIF device info, profiles
│   │   │   └── add_to_vms.py           # Add via REST Config API
│   │   │
│   │   └── bridge/                      # gRPC → Windows .NET shim
│   │       ├── __init__.py
│   │       ├── client.py                # gRPC client stub
│   │       ├── smart_search.py          # Smart Search RPC
│   │       ├── evidence_lock.py         # Evidence management
│   │       ├── privacy_masking.py       # Restricted media
│   │       ├── system_logs.py           # Log reading
│   │       ├── hardware.py              # Full hardware management
│   │       └── video_wall.py            # Matrix/video wall
│   │
│   ├── models/                          # Domain models (shared)
│   │   ├── __init__.py
│   │   ├── camera.py                    # Camera + streams
│   │   ├── alarm.py                     # Alarm
│   │   ├── bookmark.py                  # Bookmark
│   │   ├── recording.py                # Recording info
│   │   ├── event.py                     # Event
│   │   ├── user.py                      # User + roles
│   │   ├── hardware.py                  # Hardware device
│   │   └── view.py                      # View/layout definition
│   │
│   └── services/                        # Business logic layer
│       ├── __init__.py
│       ├── camera_service.py            # Camera tree, state
│       ├── alarm_service.py             # Alarm management workflow
│       ├── playback_service.py          # Playback controller
│       ├── export_service.py            # Export workflow
│       ├── ptz_service.py              # PTZ management
│       ├── sequencing_service.py        # Tour/sequence logic
│       ├── bookmark_service.py          # Bookmark CRUD
│       ├── discovery_service.py         # ONVIF discovery
│       └── bridge_service.py            # gRPC bridge orchestrator
│
├── bridge/                              # Windows .NET Bridge
│   ├── MilestoneBridge/
│   │   ├── MilestoneBridge.csproj
│   │   ├── Program.cs                   # gRPC server startup
│   │   ├── Services/
│   │   │   ├── SmartSearchService.cs
│   │   │   ├── EvidenceService.cs
│   │   │   ├── PrivacyMaskingService.cs
│   │   │   ├── HardwareService.cs
│   │   │   ├── SystemService.cs
│   │   │   └── VideoWallService.cs
│   │   ├── Protos/
│   │   │   └── bridge.proto
│   │   └── SdkProxy.cs                  # Wraps VideoOS.Platform.SDK calls
│   └── Bridge.sln
│
├── proto/                               # Shared gRPC protobuf definitions
│   └── bridge.proto
│
└── scripts/
    ├── onvif_discover.py                # Standalone ONVIF scanner
    └── deploy_bridge.ps1               # Windows bridge deployment script
```

---

## Protocol Adapter Detail

### REST API Gateway (`/REST/v1/`)
- **Auth**: OAuth2 Bearer token via OIDC password grant / windows_credentials grant
- **Base client**: httpx.AsyncClient with token refresh
- **Base URL**: `https://{server}/api`
- **Coverage**: Config CRUD, Alarms, Events, Bookmarks, WebRTC session life cycle

### Mobile XML-RPC (`/XProtectMobile/Communication`)
- **Auth**: Custom Diffie-Hellman key exchange → CHAP challenge-response → session cookie
- **Wire format**: XML over HTTP POST
- **Key exchange flow**:
  1. `Connect` → server sends DH prime + generator + server public key
  2. Client generates key pair, computes shared secret
  3. `LogIn` → client sends username + CHAP hash(password, challenge) encrypted with AES(shared_secret)
  4. Server returns session cookie used for all subsequent requests
- **All calls** use `<Communication><ConnectionId>...<Command SequenceId="N">...</Command></Communication>` XML
- **Reimplement** from XPMobileSDK.js `Connection.js`, `ConnectionRequest.js`, `ConnectionResponse.js`

### WebRTC Pipeline (aiortc)
- **Initiation**: REST POST to create session, get offer SDP
- **Signaling**: REST-based (PATCH answer SDP, GET/POST ICE candidates)
- **Media**: aiortc RTCPeerConnection → video track → frame callback
- **Frame → UI**: aiortc fires `track.recv()` → convert to QImage → emit via Qt signal → QWidget paint
- **PTZ**: WebRTC data channel with JSON: `{ApiVersion:"1.0",type:"request",method:"ptzMove",params:{direction:"up"}}`
- **Playback**: Pass `playbackTime`, `speed`, `skipGaps` params on session init
- **Multi-camera**: One RTCPeerConnection per camera in the grid view

### gRPC Bridge → Windows .NET Shim
- **Proto service**:

```protobuf
service MilestoneBridge {
  // Smart Search
  rpc StartMotionSearch(MotionSearchRequest) returns (MotionSearchResult);
  rpc GetMotionSearchProgress(ProgressRequest) returns (ProgressResponse);
  
  // Evidence Lock
  rpc LockEvidence(EvidenceRequest) returns (EvidenceResponse);
  rpc UnlockEvidence(EvidenceRequest) returns (EvidenceResponse);
  rpc GetLockedEvidence(EvidenceListRequest) returns (EvidenceListResponse);
  
  // Privacy Masking
  rpc GetRestrictedMedia(RestrictedMediaRequest) returns (RestrictedMediaResponse);
  
  // Hardware Management
  rpc ScanHardware(HardwareScanRequest) returns (HardwareScanResponse);
  rpc AddHardware(HardwareAddRequest) returns (HardwareAddResponse);
  rpc RemoveHardware(HardwareRemoveRequest) returns (Empty);
  rpc FirmwareUpdate(FirmwareRequest) returns (FirmwareResponse);
  
  // System
  rpc GetSystemLogs(LogQuery) returns (LogResponse);
  rpc GetSystemStatus(Empty) returns (SystemStatusResponse);
  rpc GetRecordingServerStatus(Empty) returns (RecordingServerStatus);
  
  // Video Wall
  rpc GetVideoWalls(Empty) returns (VideoWallList);
  rpc SendToVideoWall(VideoWallCommand) returns (Empty);
  
  // PTZ Tours/Patrols
  rpc GetPatrols(PatrolQuery) returns (PatrolList);
  rpc StartPatrol(PatrolCommand) returns (Empty);
  rpc StopPatrol(PatrolCommand) returns (Empty);
}
```

---

## Data Flow: Live Video (Single Camera)

```
User clicks camera in tree
        │
        ▼
CameraService.get_camera_device_id(camera_id)
        │
        ▼
WebRTCRestClient.create_session(device_id, options)
  POST /REST/v1/WebRTC/Session  →  { sessionId, offerSDP }
        │
        ▼
WebRTCEngine.create_peer_connection()
  aiortc RTCPeerConnection(iceServers)
        │
        ▼
WebRTCEngine.set_remote_description(offerSDP)
  ▶ createAnswer()
  ▶ set_local_description(answerSDP)
        │
        ▼
WebRTCRestClient.update_answer_sdp(session_id, answerSDP)
  PATCH /REST/v1/WebRTC/Session/{id}
        │
        ▼
(ICE candidate exchange via polling)
  GET  /REST/v1/WebRTC/IceCandidates/{id}  →  candidate[]
  POST /REST/v1/WebRTC/IceCandidates/{id}  ←  local_candidate
        │
        ▼
(Connection established)
  video_track = peerConnection.addTrack(video)
  video_track.on_frame(frame)
        │
        ▼
VideoRenderer.frame_received(frame)
  ▶ Convert to QImage
  ▶ Emit pyqtSignal(new_frame: QImage)
        │
        ▼
CameraViewWidget.on_frame(frame)
  ▶ update()
  ▶ paintEvent → draw QImage on QPainter
```

---

## Data Flow: Sequence/Tour

```
User activates sequence
        │
        ▼
SequencingService.start_sequence(view_id)
        │
        ▼
MobileXMLRPC.sequences.get_next_sequence(view_id)
  POST /XProtectMobile/Communication
  <Command><Name>GetNextSequence</Name></Command>
  Response: { nextDeviceId, nextCameraName }
        │
        ▼
WebRTCEngine.ChangeStream(new_device_id)
  (no new session -- Mobile protocol handles this:
   <Command><Name>ChangeStream</Name></Command>)
        │
        ▼
(Sequence interval timer fires)
MobileXMLRPC.sequences.get_next_sequence(view_id)
  ▶ ChangeStream to new device_id
```

---

## Data Flow: Smart Search (via Bridge)

```
User draws rectangle on playback video
        │
        ▼
SmartSearchService.start_motion_search(
  camera_id, start_time, end_time,
  roi_x, roi_y, roi_w, roi_h
)
        │
        ▼
gRPC Bridge: StartMotionSearch { camera, timeRange, region }
        │
        ▼
[Windows Bridge Server]
  SessionHelper.Login(server, user, pass)
  session.Configuration.Get<Camera>(camera_id)
  SmartSearchSession.BeginSearch(camera, timeRange, region)
  ▶ returns task ID
        │
        ▼
Poll: GetMotionSearchProgress(task_id)
  ▶ returns { progress%, results[] }
        │
        ▼
Results flow back through gRPC:
  results[] = { timestamp, x, y, w, h, confidence }
UI marks motion regions on timeline
```

---

## Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)
```
Goal: Single camera live view on Linux
- Project scaffold, PySide6 main window with camera tree
- OAuth2 auth + REST client
- WebRTC REST session initiation
- aiortc pipeline → frame → QImage → QWidget
- Connect to real XProtect, see live video
```

### Phase 2: Mobile XML-RPC (Weeks 3-4)
```
Goal: Camera tree, PTZ, thumbnails
- DH key exchange + CHAP auth implementation
- Camera tree enumeration (GetAllViews)
- PTZ presets + recall via Mobile protocol
- Thumbnails grid widget
```

### Phase 3: Playback + Timeline (Weeks 5-6)
```
Goal: Full playback experience
- Playback WebRTC session (playbackTime param)
- Timeline widget (PySide6 custom graphics)
- Speed control + skip-gaps
- Multi-camera playback
- Bookmark nav (REST + timeline markers)
```

### Phase 4: Advanced Features (Weeks 7-10)
```
Goal: Parity on Mobile protocol features
- Sequences/tours + carousel mode
- Two-way audio / push-to-talk
- Export investigations workflow
- Alarm panel (REST + WebSocket live events)
- WebSocket Event & State subscription
```

### Phase 5: Windows Bridge (Weeks 11-14)
```
Goal: Close the .NET gap
- .NET 8 gRPC bridge server (deploy on Recording Server)
- Smart Search (UI + bridge call)
- Evidence lock management
- ONVIF discovery (direct from Linux + bridge for VMS add)
- Video wall control
- System log viewer
- Privacy masking integration
```

### Phase 6: Polish (Weeks 15-18)
```
Goal: Production quality
- Map widget (Leaflet/OSM via QtWebEngine)
- Keyboard shortcuts
- Hardware decoding optimization
- Connection management (reconnect, multi-server)
- Settings dialog, profiles, persistent config
- Packaging (AppImage, .deb, .rpm)
- Bridge deployment script
```

---

## Appendix: Dependency Map

```
PySide6              → UI framework
httpx                → Async HTTP (REST + Mobile XML-RPC)
aiortc               → WebRTC (pip install aiortc)
av                   → Frame decoding (pip install av)
websockets           → Event & State WebSocket API
grpcio               → gRPC client for Windows bridge
grpcio-tools         → Proto compilation
onvif-zeep           → ONVIF device discovery
cryptography         → DH param generation, AES encryption (Mobile auth)
pyyaml / toml        → Config files
Pillow               → Image manipulation for thumbnails
qtawesome            → Icons (optional)

Windows Bridge:
  Grpc.AspNetCore    → gRPC server
  MilestoneSystems.VideoOS.Platform.SDK  → Full .NET SDK
  MilestoneSystems.VideoOS.Platform      → Core platform
```
