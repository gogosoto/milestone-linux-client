"""
Alarm Panel — list and acknowledge alarms
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLabel,
)
from PySide6.QtCore import Qt
from src.core.event_bus import event_bus


class AlarmPanel(QWidget):
    """Alarm list panel with acknowledge actions."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        # Header
        header = QHBoxLayout()
        header.addWidget(QLabel("Alarms"))
        self._count_label = QLabel("0 unacknowledged")
        header.addWidget(self._count_label)
        header.addStretch()
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self._on_refresh)
        header.addWidget(refresh_btn)
        layout.addLayout(header)

        # Table
        self._table = QTableWidget(0, 4)
        self._table.setHorizontalHeaderLabels(["Time", "Priority", "Camera", "State"])
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self._table)

        # Actions
        actions = QHBoxLayout()
        ack_btn = QPushButton("Acknowledge")
        ack_btn.clicked.connect(self._on_acknowledge)
        actions.addWidget(ack_btn)
        actions.addStretch()
        layout.addLayout(actions)

    def _on_refresh(self):
        event_bus.status_message.emit("Refreshing alarms...")

    def _on_acknowledge(self):
        selected = self._table.currentRow()
        if selected >= 0:
            alarm_id = self._table.item(selected, 0).data(Qt.UserRole)
            if alarm_id:
                event_bus.status_message.emit(f"Acknowledging alarm {alarm_id}...")
