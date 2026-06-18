"""
Domain models shared across the application
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Camera:
    id: str
    name: str
    device_id: str
    group_id: str = ""
    is_ptz: bool = False
    is_online: bool = True
    recording_server_id: str = ""
    ip_address: str = ""
    model: str = ""
    manufacturer: str = ""


@dataclass
class CameraGroup:
    id: str
    name: str
    parent_id: str = ""
    cameras: list[Camera] = field(default_factory=list)
    subgroups: list["CameraGroup"] = field(default_factory=list)


@dataclass
class Alarm:
    id: str
    name: str
    priority: int = 0
    state: str = "New"  # New, Acknowledged, Locked
    time: datetime = field(default_factory=datetime.now)
    camera_id: str = ""
    camera_name: str = ""
    assigned_user: str = ""
    description: str = ""


@dataclass
class Bookmark:
    id: str
    camera_id: str
    time: datetime
    description: str = ""
    duration: float = 0.0


@dataclass
class Recording:
    camera_id: str
    start_time: datetime
    end_time: datetime
    is_live: bool = True
    storage: str = ""


@dataclass
class PTZPreset:
    id: str
    name: str
    camera_id: str
    index: int = 0


@dataclass
class Patrol:
    id: str
    name: str
    camera_id: str
    presets: list[PTZPreset] = field(default_factory=list)
    speed: int = 50
    dwell_time: int = 5


@dataclass
class ViewLayout:
    id: str
    name: str
    grid_cols: int = 1
    grid_rows: int = 1
    cameras: list[str] = field(default_factory=list)  # camera_ids in grid order


@dataclass
class Sequence:
    id: str
    name: str
    view_id: str
    camera_ids: list[str] = field(default_factory=list)
    dwell_time: int = 10


@dataclass
class ExportJob:
    id: str
    camera_id: str
    start_time: datetime
    end_time: datetime
    status: str = "Pending"  # Pending, InProgress, Complete, Failed
    format: str = "mp4"
    download_url: str = ""
    progress: float = 0.0


@dataclass
class SystemStatus:
    status: str = "OK"
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    disk_usage: float = 0.0
    active_sessions: int = 0
    rec_server_name: str = ""
    rec_server_status: str = ""
