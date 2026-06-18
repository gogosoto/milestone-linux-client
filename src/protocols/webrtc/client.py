"""
WebRTC media pipeline using aiortc

Manages RTCPeerConnection lifecycle, SDP signaling, ICE negotiation,
frame capture, and PTZ data channel.
"""
import asyncio
import json
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCIceCandidate
from aiortc.mediastreams import VideoFrame
from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QImage
from src.protocols.rest_api.webrtc import WebRTCRestClient


class WebRTCEngine(QObject):
    """Single WebRTC peer connection for one camera stream."""

    frame_received = Signal(str, object)  # camera_id, QImage
    connection_state_changed = Signal(str, str)  # camera_id, state

    def __init__(self, rest_webrtc: WebRTCRestClient, camera_id: str):
        super().__init__()
        self._rest = rest_webrtc
        self.camera_id = camera_id
        self._pc: RTCPeerConnection | None = None
        self._session_id: str | None = None
        self._data_channel = None
        self._candidates_seen: set[str] = set()
        self._running = False

    async def start(self, device_id: str, *,
                    playback_time: str | None = None,
                    speed: float | None = None,
                    skip_gaps: bool = False,
                    include_audio: bool = True):
        """Full WebRTC session init: REST offer → answer → ICE."""
        self._pc = RTCPeerConnection()
        self._setup_handlers()

        # 1. REST: create WebRTC session → get server SDP offer
        session = await self._rest.create_session(
            device_id, include_audio=include_audio,
            playback_time=playback_time, speed=speed, skip_gaps=skip_gaps,
        )
        self._session_id = session["sessionId"]
        offer_sdp = session.get("offerSDP", session.get("OfferSDP", ""))
        if isinstance(offer_sdp, str):
            offer = RTCSessionDescription(type="offer", sdp=offer_sdp)
        elif isinstance(offer_sdp, dict):
            offer = RTCSessionDescription(
                type=offer_sdp.get("type", "offer"),
                sdp=offer_sdp.get("sdp", ""),
            )
        else:
            raise TypeError(f"Unexpected offerSDP type: {type(offer_sdp)}")

        await self._pc.setRemoteDescription(offer)

        # 2. Create + set local SDP answer
        answer = await self._pc.createAnswer()
        await self._pc.setLocalDescription(answer)

        # 3. Send answer SDP to server
        answer_json = json.dumps({
            "type": "answer",
            "sdp": self._pc.localDescription.sdp,
        })
        await self._rest.update_answer_sdp(self._session_id, answer_json)

        # 4. Start ICE candidate polling
        self._running = True
        asyncio.ensure_future(self._poll_ice())

        # 5. Create PTZ data channel
        self._data_channel = self._pc.createDataChannel(
            "commands", protocol="videoos-commands"
        )

    async def stop(self):
        self._running = False
        if self._pc:
            await self._pc.close()
            self._pc = None
        self._session_id = None

    async def send_ptz(self, direction: str):
        if self._data_channel and self._data_channel.readyState == "open":
            self._data_channel.send(json.dumps({
                "ApiVersion": "1.0", "type": "request",
                "method": "ptzMove",
                "params": {"direction": direction},
            }))

    async def send_aux(self, aux_number: str, state: bool):
        if self._data_channel and self._data_channel.readyState == "open":
            self._data_channel.send(json.dumps({
                "ApiVersion": "1.0", "type": "request",
                "method": "setAux",
                "params": {"on": state, "auxNumber": aux_number},
            }))

    def _setup_handlers(self):
        @self._pc.on("track")
        async def on_track(track):
            if track.kind == "video":
                while True:
                    try:
                        frame: VideoFrame = await track.recv()
                        qimg = self._frame_to_qimage(frame)
                        self.frame_received.emit(self.camera_id, qimg)
                    except Exception:
                        break

        @self._pc.on("iceconnectionstatechange")
        def on_ice():
            state = self._pc.iceConnectionState if self._pc else "closed"
            self.connection_state_changed.emit(self.camera_id, state)

        @self._pc.on("connectionstatechange")
        def on_conn():
            state = self._pc.connectionState if self._pc else "closed"
            self.connection_state_changed.emit(self.camera_id, state)

    async def _poll_ice(self):
        """Poll server for ICE candidates (every 500ms)."""
        while self._running and self._session_id and self._pc:
            try:
                data = await self._rest.get_ice_candidates(self._session_id)
                candidates = data.get("candidates", [])
                for c_str in candidates:
                    if c_str not in self._candidates_seen:
                        self._candidates_seen.add(c_str)
                        cd = json.loads(c_str) if isinstance(c_str, str) else c_str
                        candidate = RTCIceCandidate(
                            component=cd.get("component", 1),
                            foundation=cd.get("foundation", "0"),
                            ip=cd.get("ip", ""),
                            port=cd.get("port", 0),
                            priority=cd.get("priority", 0),
                            protocol=cd.get("protocol", "udp"),
                            type=cd.get("type", "host"),
                        )
                        await self._pc.addIceCandidate(candidate)
            except Exception:
                pass
            await asyncio.sleep(0.5)

    @staticmethod
    def _frame_to_qimage(frame: VideoFrame) -> QImage:
        """Convert aiortc VideoFrame to QImage."""
        img = frame.to_image()  # returns PIL Image
        if img.mode == "RGB":
            data = img.tobytes("raw", "RGB")
            return QImage(data, img.width, img.height, QImage.Format_RGB888)
        elif img.mode == "RGBA":
            data = img.tobytes("raw", "RGBA")
            return QImage(data, img.width, img.height, QImage.Format_RGBA8888)
        else:
            img = img.convert("RGB")
            data = img.tobytes("raw", "RGB")
            return QImage(data, img.width, img.height, QImage.Format_RGB888)
