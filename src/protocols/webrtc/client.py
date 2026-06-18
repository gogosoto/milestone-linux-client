"""
WebRTC media pipeline using aiortc

Handles:
- RTCPeerConnection lifecycle (per camera stream)
- SDP offer/answer exchange via REST
- ICE candidate negotiation
- Frame capture → QImage emission
- PTZ data channel
"""
import asyncio
import json
from typing import Callable
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCIceCandidate
from aiortc.mediastreams import VideoFrame
from PySide6.QtCore import QObject, Signal
from src.protocols.rest_api.webrtc import WebRTCRestClient


class WebRTCEngine(QObject):
    """Manages a single WebRTC peer connection for one camera stream."""

    frame_received = Signal(str, object)  # camera_id, QImage
    connection_state_changed = Signal(str, str)  # camera_id, new_state
    ptz_response = Signal(str, object)  # camera_id, response_data

    def __init__(self, rest_webrtc: WebRTCRestClient, camera_id: str,
                 ice_servers: list[dict] | None = None):
        super().__init__()
        self._rest = rest_webrtc
        self.camera_id = camera_id
        self._pc: RTCPeerConnection | None = None
        self._session_id: str | None = None
        self._data_channel = None
        self._ice_servers = ice_servers or []
        self._candidates_seen: set[str] = set()

    async def start(self, device_id: str, *, playback_time: str | None = None,
                    speed: float | None = None, skip_gaps: bool = False,
                    include_audio: bool = True):
        """Full WebRTC session initiation."""
        # 1. Create peer connection
        self._pc = RTCPeerConnection()
        self._setup_handlers()

        # 2. Initiate session via REST → get offer SDP
        session = await self._rest.create_session(
            device_id,
            include_audio=include_audio,
            playback_time=playback_time,
            speed=speed,
            skip_gaps=skip_gaps,
            ice_servers=self._ice_servers,
        )
        self._session_id = session["sessionId"]
        offer = RTCSessionDescription(
            type="offer", sdp=session["offerSDP"]
        )
        await self._pc.setRemoteDescription(offer)

        # 3. Create + set local answer
        answer = await self._pc.createAnswer()
        await self._pc.setLocalDescription(answer)

        # 4. Send answer SDP to server
        await self._rest.update_answer_sdp(
            self._session_id, json.dumps({"type": "answer", "sdp": answer.sdp})
        )

        # 5. Start ICE candidate polling
        asyncio.ensure_future(self._poll_ice_candidates())

        # 6. Create data channel for PTZ
        self._data_channel = self._pc.createDataChannel("commands", {
            "protocol": "videoos-commands"
        })

    async def stop(self):
        """Close the peer connection."""
        if self._pc:
            await self._pc.close()
            self._pc = None
        self._session_id = None

    async def send_ptz_command(self, direction: str):
        """Send PTZ move command via WebRTC data channel."""
        if self._data_channel and self._data_channel.readyState == "open":
            cmd = {
                "ApiVersion": "1.0",
                "type": "request",
                "method": "ptzMove",
                "params": {"direction": direction},
            }
            self._data_channel.send(json.dumps(cmd))

    async def send_aux_command(self, aux_number: str, state: bool):
        """Send auxiliary command via data channel."""
        if self._data_channel and self._data_channel.readyState == "open":
            cmd = {
                "ApiVersion": "1.0",
                "type": "request",
                "method": "setAux",
                "params": {"on": state, "auxNumber": aux_number},
            }
            self._data_channel.send(json.dumps(cmd))

    def _setup_handlers(self):
        @self._pc.on("track")
        async def on_track(track):
            if track.kind == "video":
                while True:
                    try:
                        frame = await track.recv()
                        # Convert aiortc VideoFrame to QImage
                        qimg = self._frame_to_qimage(frame)
                        self.frame_received.emit(self.camera_id, qimg)
                    except Exception:
                        break

        @self._pc.on("iceconnectionstatechange")
        def on_ice_state():
            state = self._pc.iceConnectionState if self._pc else "closed"
            self.connection_state_changed.emit(self.camera_id, state)

    async def _poll_ice_candidates(self):
        """Poll server for ICE candidates (REST-based signaling)."""
        while self._session_id and self._pc:
            try:
                data = await self._rest.get_ice_candidates(self._session_id)
                candidates = data.get("candidates", [])
                for candidate_str in candidates:
                    if candidate_str not in self._candidates_seen:
                        self._candidates_seen.add(candidate_str)
                        candidate_dict = json.loads(candidate_str)
                        candidate = RTCIceCandidate(
                            component=candidate_dict.get("component", 1),
                            foundation=candidate_dict.get("foundation", "0"),
                            ip=candidate_dict.get("ip", ""),
                            port=candidate_dict.get("port", 0),
                            priority=candidate_dict.get("priority", 0),
                            protocol=candidate_dict.get("protocol", "udp"),
                            type=candidate_dict.get("type", "host"),
                        )
                        await self._pc.addIceCandidate(candidate)
            except Exception:
                pass
            await asyncio.sleep(0.5)

    @staticmethod
    def _frame_to_qimage(frame: VideoFrame) -> object:
        """Convert aiortc VideoFrame to QImage."""
        from PIL import Image
        import io
        from PySide6.QtGui import QImage

        # aiortc frames are numpy arrays (yuv420p by default)
        img = frame.to_image()  # returns PIL Image
        # Convert PIL → QImage
        with io.BytesIO() as buf:
            img.save(buf, format="RGB")
            buf.seek(0)
            qimg = QImage()
            qimg.loadFromData(buf.read(), "RGB")
        return qimg
