"""
CameraViewWidget — renders a single camera's WebRTC video stream
"""
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtGui import QPainter, QImage, QColor, QFont
from PySide6.QtCore import Qt
from src.core.event_bus import event_bus


class CameraViewWidget(QWidget):
    """Widget that displays a single camera's video stream."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.camera_id: str | None = None
        self._camera_name: str = ""
        self._frame: QImage | None = None
        self._loading = False
        self._is_playing = False
        self.setMinimumSize(160, 120)
        self.setStyleSheet("background-color: #1a1a1a; border: 1px solid #333;")
        event_bus.video_frame.connect(self._on_frame)

    def set_camera(self, camera_id: str, name: str = ""):
        self.camera_id = camera_id
        self._camera_name = name
        self._loading = True
        self.update()

    async def start_stream(self, session, device_id: str):
        """Connect WebRTC and begin displaying video."""
        from src.protocols.webrtc.session_manager import WebRTCSessionManager
        manager = WebRTCSessionManager(session.rest.webrtc)
        engine = await manager.start_camera(self.camera_id or device_id, device_id)
        engine.frame_received.connect(self._on_webrtc_frame)
        self._loading = False
        self._is_playing = True
        self.set_camera(device_id)

    def _on_webrtc_frame(self, camera_id: str, qimg: QImage):
        if camera_id == self.camera_id:
            self._frame = qimg
            self.update()

    def _on_frame(self, camera_id: str, qimg: QImage):
        """Receive video frame from event bus."""
        if camera_id == self.camera_id:
            self._frame = qimg
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        if self._frame and not self._frame.isNull():
            # Scale to fit maintaining aspect ratio
            scaled = self._frame.scaled(
                self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            x = (self.width() - scaled.width()) // 2
            y = (self.height() - scaled.height()) // 2
            painter.drawImage(x, y, scaled)
        else:
            # Placeholder
            painter.fillRect(self.rect(), QColor("#1a1a1a"))
            painter.setPen(QColor("#666"))
            if self._loading:
                painter.drawText(self.rect(), Qt.AlignCenter, "Connecting...")
            elif self.camera_id:
                painter.drawText(self.rect(), Qt.AlignCenter, self._camera_name or self.camera_id)
            else:
                painter.drawText(self.rect(), Qt.AlignCenter, "No Camera")
