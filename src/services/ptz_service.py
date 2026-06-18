"""
PTZ service — PTZ control, presets, patrols
"""
from src.protocols.webrtc.session_manager import WebRTCSessionManager
from src.protocols.bridge.client import BridgeClient
from src.models import PTZPreset


class PTZService:
    def __init__(self, webrtc: WebRTCSessionManager, bridge: BridgeClient | None = None):
        self._webrtc = webrtc
        self._bridge = bridge
        self._presets: dict[str, list[PTZPreset]] = {}

    async def move(self, camera_id: str, direction: str):
        """Move PTZ camera in a direction (up, down, left, right, etc.)."""
        await self._webrtc.send_ptz(camera_id, direction)

    async def stop(self, camera_id: str):
        await self._webrtc.send_ptz(camera_id, "stop")

    async def home(self, camera_id: str):
        await self._webrtc.send_ptz(camera_id, "home")

    async def zoom(self, camera_id: str, direction: str = "in"):
        await self._webrtc.send_ptz(camera_id, f"zoom{direction}")

    async def set_preset(self, camera_id: str, preset_name: str, index: int):
        preset = PTZPreset(id=f"{camera_id}_{index}", name=preset_name,
                          camera_id=camera_id, index=index)
        if camera_id not in self._presets:
            self._presets[camera_id] = []
        self._presets[camera_id].append(preset)
        # TODO: save preset via Mobile protocol

    async def recall_preset(self, camera_id: str, index: int):
        await self._webrtc.send_ptz(camera_id, f"preset{index}")

    async def aux(self, camera_id: str, aux_number: str, state: bool):
        await self._webrtc.send_aux(camera_id, aux_number, state)

    async def get_patrols(self, camera_id: str, server_creds: dict) -> list[dict]:
        """Get PTZ patrols (requires bridge)."""
        if self._bridge:
            return await self._bridge.get_patrols(**server_creds, camera_id=camera_id)
        return []

    async def start_patrol(self, camera_id: str, patrol_id: str, server_creds: dict):
        if self._bridge:
            await self._bridge.start_patrol(**server_creds, camera_id=camera_id,
                                            patrol_id=patrol_id)

    async def stop_patrol(self, camera_id: str, patrol_id: str, server_creds: dict):
        if self._bridge:
            await self._bridge.stop_patrol(**server_creds, camera_id=camera_id,
                                           patrol_id=patrol_id)
