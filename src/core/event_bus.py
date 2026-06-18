"""
In-app event bus using PySide6 signals
"""
from PySide6.QtCore import QObject, Signal


class EventBus(QObject):
    """Central event bus for decoupled UI ↔ service communication."""
    # Connection events
    connected = Signal(str)          # server_name
    disconnected = Signal(str)       # server_name
    connection_error = Signal(str, str)  # server_name, error_msg

    # Camera events
    camera_selected = Signal(str)    # camera_id
    camera_deselected = Signal(str)  # camera_id
    cameras_updated = Signal(list)   # list[Camera]

    # Video events
    video_frame = Signal(str, object)  # camera_id, QImage
    video_playing = Signal(str)        # camera_id
    video_paused = Signal(str)         # camera_id
    video_stopped = Signal(str)        # camera_id

    # Playback events
    playback_time_changed = Signal(float)   # timestamp
    playback_speed_changed = Signal(float)  # speed multiplier

    # Alarm events
    alarm_received = Signal(object)     # Alarm
    alarm_updated = Signal(object)      # Alarm

    # PTZ events
    ptz_command_sent = Signal(str, str)  # camera_id, command

    # Bridge events
    bridge_connected = Signal()
    bridge_disconnected = Signal()
    bridge_error = Signal(str)

    # Generic
    status_message = Signal(str)       # status bar text
    error_occurred = Signal(str)       # error dialog trigger


event_bus = EventBus()
