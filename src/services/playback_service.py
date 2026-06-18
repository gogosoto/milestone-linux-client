"""
Playback service — playback controls, timeline management
"""
from src.protocols.mobile_xmlrpc.connection import MobileConnection
from src.protocols.rest_api.bookmarks import BookmarksAPI
from src.protocols.webrtc.session_manager import WebRTCSessionManager


class PlaybackService:
    def __init__(self, mobile: MobileConnection, bookmarks: BookmarksAPI,
                 webrtc: WebRTCSessionManager):
        self._mobile = mobile
        self._bookmarks = bookmarks
        self._webrtc = webrtc
        self._speed: float = 1.0
        self._is_playing: bool = False
        self._current_time: float = 0.0

    async def seek_to(self, camera_id: str, timestamp: str):
        """Seek playback to a specific time."""
        await self._mobile.create_playback_controller(camera_id, timestamp)
        self._current_time = timestamp

    async def set_speed(self, speed: float):
        self._speed = speed

    async def get_bookmarks(self, camera_id: str | None = None) -> list[dict]:
        return await self._bookmarks.list_bookmarks(camera_id)

    async def create_bookmark(self, camera_id: str, time: str, desc: str = ""):
        return await self._bookmarks.create_bookmark(camera_id, time, desc)

    @property
    def speed(self) -> float:
        return self._speed

    @property
    def is_playing(self) -> bool:
        return self._is_playing
