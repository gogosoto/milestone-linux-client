"""
CameraViewWidget — displays a single camera's video stream

Supports both WebRTC (aiortc) and ImageServer TCP protocol.
WebRTC is preferred when the API Gateway has it enabled.
ImageServer falls back to the Recording Server's TCP stream.
"""
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QImage, QColor
from PySide6.QtCore import Qt
from src.core.event_bus import event_bus


class CameraViewWidget(QWidget):
    """Single camera view with video rendering."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.camera_id: str | None = None
        self._frame: QImage | None = None
        self._status_text = "No Camera"
        self._is_playing = False
        self._engine = None
        self.setMinimumSize(160, 120)
        self.setStyleSheet("background-color: #1a1a1a; border: 1px solid #333;")

    async def start_stream(self, session, camera_id: str):
        """Start video stream — tries WebRTC first, falls back to ImageServer."""
        self.camera_id = camera_id
        self._status_text = "Connecting..."
        self.update()

        # Try WebRTC first
        try:
            from src.protocols.webrtc.session_manager import WebRTCSessionManager
            manager = WebRTCSessionManager(session.rest.webrtc)
            engine = await manager.start_camera(camera_id, camera_id)
            engine.frame_received.connect(self._on_frame)
            engine.connection_state_changed.connect(self._on_state)
            self._engine = engine
            self._is_playing = True
            self._status_text = "Connected (WebRTC)"
            return
        except Exception as e:
            self._status_text = f"WebRTC failed, trying ImageServer..."

        # Fallback to ImageServer TCP protocol
        try:
            from src.protocols.imageserver.client import ImageServerClient
            import re

            # Get recording server info from REST API
            rs_list = await session.config_api.get_recording_servers()
            if not rs_list:
                raise Exception("No recording servers found")
            rs = rs_list[0]
            rs_host = rs.get("hostName", rs.get("name", ""))
            rs_port = rs.get("portNumber", 7563)

            client = ImageServerClient(rs_host, rs_port)
            client.frame_received.connect(self._on_frame)
            client.connection_state.connect(self._on_state)
            self._engine = client

            token = session.auth.token
            await client.connect_live(camera_id, token)
            self._is_playing = True
        except Exception as e:
            self._status_text = f"Failed: {e}"
            self.update()

    async def stop_stream(self):
        if self._engine:
            if hasattr(self._engine, 'stop'):
                await self._engine.stop()
            elif hasattr(self._engine, 'stop_all'):
                await self._engine.stop_all()
        self._engine = None
        self._is_playing = False
        self._frame = None
        self.camera_id = None
        self._status_text = "No Camera"
        self.update()

    def _on_frame(self, cam_id: str, qimg: QImage):
        if cam_id == self.camera_id and qimg and not qimg.isNull():
            self._frame = qimg
            self.update()

    def _on_state(self, cam_id: str, state: str):
        if cam_id == self.camera_id:
            self._status_text = state
            self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.SmoothPixmapTransform)
        if self._frame and not self._frame.isNull():
            scaled = self._frame.scaled(
                self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            x = (self.width() - scaled.width()) // 2
            y = (self.height() - scaled.height()) // 2
            p.drawImage(x, y, scaled)
        else:
            p.fillRect(self.rect(), QColor("#1a1a1a"))
            p.setPen(QColor("#888"))
            p.drawText(self.rect(), Qt.AlignCenter, self._status_text)
