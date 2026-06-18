"""
CameraViewWidget — displays a single camera's WebRTC video stream

Phase 1: Connect WebRTC → receive frames → render as QImage
"""
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QImage, QColor
from PySide6.QtCore import Qt, Signal
from src.core.event_bus import event_bus


class CameraViewWidget(QWidget):
    """Single camera view with WebRTC video rendering."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.camera_id: str | None = None
        self._camera_name: str = ""
        self._frame: QImage | None = None
        self._status_text = "No Camera"
        self._is_playing = False
        self.setMinimumSize(160, 120)
        self.setStyleSheet("background-color: #1a1a1a; border: 1px solid #333;")

    def set_status(self, text: str):
        self._status_text = text
        self.update()

    async def start_stream(self, session, camera_id: str):
        """Connect WebRTC for this camera and start receiving frames."""
        self.camera_id = camera_id
        self._status_text = "Connecting..."
        self.update()

        from src.protocols.webrtc.session_manager import WebRTCSessionManager
        manager = WebRTCSessionManager(session.rest.webrtc)
        engine = await manager.start_camera(camera_id, camera_id)
        engine.frame_received.connect(self._on_frame)
        engine.connection_state_changed.connect(self._on_connection_state)
        self._is_playing = True
        self._status_text = "Connected"

    def _on_frame(self, cam_id: str, qimg: QImage):
        if cam_id == self.camera_id and qimg and not qimg.isNull():
            self._frame = qimg
            self.update()

    def _on_connection_state(self, cam_id: str, state: str):
        if cam_id == self.camera_id:
            self._status_text = state
            self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.SmoothPixmapTransform)

        if self._frame and not self._frame.isNull():
            scaled = self._frame.scaled(
                self.size(), Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            x = (self.width() - scaled.width()) // 2
            y = (self.height() - scaled.height()) // 2
            p.drawImage(x, y, scaled)
        else:
            p.fillRect(self.rect(), QColor("#1a1a1a"))
            p.setPen(QColor("#888"))
            p.drawText(self.rect(), Qt.AlignCenter, self._status_text)
