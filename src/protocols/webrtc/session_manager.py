"""
WebRTC Session Manager — manages N concurrent WebRTC sessions for multi-view
"""
from src.protocols.webrtc.client import WebRTCEngine


class WebRTCSessionManager:
    """Manages multiple WebRTC peer connections (one per camera in the grid)."""

    def __init__(self, rest_webrtc):
        self._rest = rest_webrtc
        self._sessions: dict[str, WebRTCEngine] = {}

    async def start_camera(self, camera_id: str, device_id: str,
                           **kwargs) -> WebRTCEngine:
        """Start a WebRTC session for a camera."""
        engine = WebRTCEngine(self._rest, camera_id)
        await engine.start(device_id, **kwargs)
        self._sessions[camera_id] = engine
        return engine

    async def stop_camera(self, camera_id: str):
        """Stop a camera's WebRTC session."""
        if camera_id in self._sessions:
            await self._sessions[camera_id].stop()
            del self._sessions[camera_id]

    async def stop_all(self):
        """Stop all WebRTC sessions."""
        for camera_id in list(self._sessions.keys()):
            await self.stop_camera(camera_id)

    def get(self, camera_id: str) -> WebRTCEngine | None:
        return self._sessions.get(camera_id)

    def active_count(self) -> int:
        return len(self._sessions)

    async def send_ptz(self, camera_id: str, direction: str):
        engine = self.get(camera_id)
        if engine:
            await engine.send_ptz_command(direction)

    async def send_aux(self, camera_id: str, aux_number: str, state: bool):
        engine = self.get(camera_id)
        if engine:
            await engine.send_aux_command(aux_number, state)
