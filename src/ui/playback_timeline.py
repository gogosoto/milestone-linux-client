"""
Playback Timeline — slider, speed, playback controls
"""
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QSlider, QLabel, QDoubleSpinBox,
)
from PySide6.QtCore import Qt
from src.core.event_bus import event_bus


class PlaybackTimeline(QWidget):
    """Playback control bar with timeline slider and speed controls."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)

        # Timeline slider
        slider_layout = QHBoxLayout()
        self._time_label = QLabel("00:00:00")
        slider_layout.addWidget(self._time_label)

        self._slider = QSlider(Qt.Horizontal)
        self._slider.setRange(0, 1000)
        slider_layout.addWidget(self._slider)

        self._end_time_label = QLabel("00:00:00")
        slider_layout.addWidget(self._end_time_label)
        layout.addLayout(slider_layout)

        # Controls
        ctrl_layout = QHBoxLayout()
        play_btn = QPushButton("▶")
        play_btn.clicked.connect(lambda: event_bus.status_message.emit("Play"))
        ctrl_layout.addWidget(play_btn)

        pause_btn = QPushButton("⏸")
        pause_btn.clicked.connect(lambda: event_bus.status_message.emit("Pause"))
        ctrl_layout.addWidget(pause_btn)

        stop_btn = QPushButton("⏹")
        stop_btn.clicked.connect(lambda: event_bus.status_message.emit("Stop"))
        ctrl_layout.addWidget(stop_btn)

        ctrl_layout.addStretch()
        ctrl_layout.addWidget(QLabel("Speed:"))

        self._speed_spin = QDoubleSpinBox()
        self._speed_spin.setRange(0.1, 64.0)
        self._speed_spin.setValue(1.0)
        self._speed_spin.setSingleStep(0.5)
        self._speed_spin.valueChanged.connect(
            lambda v: event_bus.status_message.emit(f"Speed: {v}x")
        )
        ctrl_layout.addWidget(self._speed_spin)

        layout.addLayout(ctrl_layout)
