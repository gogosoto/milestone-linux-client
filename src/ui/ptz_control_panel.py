"""
PTZ Control Panel — joystick, zoom, presets, aux buttons
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QGridLayout, QLabel, QComboBox, QGroupBox,
)
from PySide6.QtCore import Qt
from src.core.event_bus import event_bus


class PTZControlPanel(QWidget):
    """Panel with PTZ directional pad, zoom, presets, and aux controls."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._camera_id: str | None = None
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        # Camera selector
        layout.addWidget(QLabel("PTZ Camera:"))
        self._camera_combo = QComboBox()
        layout.addWidget(self._camera_combo)

        # Directional pad
        dpad = QGroupBox("Move")
        grid = QGridLayout(dpad)
        btn_up = QPushButton("▲")
        btn_down = QPushButton("▼")
        btn_left = QPushButton("◄")
        btn_right = QPushButton("►")
        btn_home = QPushButton("●")
        btn_upleft = QPushButton("◤")
        btn_upright = QPushButton("◥")
        btn_downleft = QPushButton("◣")
        btn_downright = QPushButton("◢")

        for btn in [btn_up, btn_down, btn_left, btn_right, btn_home,
                     btn_upleft, btn_upright, btn_downleft, btn_downright]:
            btn.setFixedSize(40, 40)
            btn.clicked.connect(self._on_ptz_click)

        grid.addWidget(btn_upleft, 0, 0)
        grid.addWidget(btn_up, 0, 1)
        grid.addWidget(btn_upright, 0, 2)
        grid.addWidget(btn_left, 1, 0)
        grid.addWidget(btn_home, 1, 1)
        grid.addWidget(btn_right, 1, 2)
        grid.addWidget(btn_downleft, 2, 0)
        grid.addWidget(btn_down, 2, 1)
        grid.addWidget(btn_downright, 2, 2)
        layout.addWidget(dpad)

        # Zoom
        zoom_group = QGroupBox("Zoom")
        zoom_layout = QHBoxLayout(zoom_group)
        zoom_in = QPushButton("＋")
        zoom_out = QPushButton("－")
        zoom_in.clicked.connect(lambda: self._send_ptz("zoomin"))
        zoom_out.clicked.connect(lambda: self._send_ptz("zoomout"))
        zoom_layout.addWidget(zoom_in)
        zoom_layout.addWidget(zoom_out)
        layout.addWidget(zoom_group)

        # Aux buttons
        aux_group = QGroupBox("Aux")
        aux_layout = QHBoxLayout(aux_group)
        for i in range(1, 5):
            btn = QPushButton(f"Aux {i}")
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, n=i: self._send_aux(n, checked))
            aux_layout.addWidget(btn)
        layout.addWidget(aux_group)

        # Presets
        preset_group = QGroupBox("Presets")
        preset_layout = QVBoxLayout(preset_group)
        self._preset_combo = QComboBox()
        preset_layout.addWidget(self._preset_combo)
        recall_btn = QPushButton("Go to Preset")
        recall_btn.clicked.connect(self._on_recall_preset)
        preset_layout.addWidget(recall_btn)
        layout.addWidget(preset_group)

        layout.addStretch()

    def set_camera(self, camera_id: str):
        self._camera_id = camera_id

    def _on_ptz_click(self):
        btn = self.sender()
        text = btn.text()
        direction_map = {
            "▲": "up", "▼": "down", "◄": "left", "►": "right",
            "●": "home",
            "◤": "upLeft", "◥": "upRight",
            "◣": "downLeft", "◢": "downRight",
        }
        direction = direction_map.get(text)
        if direction and self._camera_id:
            self._send_ptz(direction)

    def _send_ptz(self, direction: str):
        if self._camera_id:
            event_bus.ptz_command_sent.emit(self._camera_id, direction)

    def _send_aux(self, aux_number: int, state: bool):
        if self._camera_id:
            event_bus.status_message.emit(f"Aux {aux_number} {'on' if state else 'off'}")

    def _on_recall_preset(self):
        pass
