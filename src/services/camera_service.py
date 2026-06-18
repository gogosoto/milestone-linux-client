"""
Camera service — fetches camera list from Hardware endpoint
"""
from src.protocols.rest_api.config import ConfigAPI
from src.protocols.bridge.client import BridgeClient
from src.models import Camera, CameraGroup


class CameraService:
    def __init__(self, config_api: ConfigAPI, bridge: BridgeClient | None = None):
        self._config = config_api
        self._bridge = bridge
        self._cameras: dict[str, Camera] = {}

    async def refresh(self) -> CameraGroup:
        """Fetch all hardware devices from the REST API."""
        items = await self._config.get_hardware()
        root = CameraGroup(id="root", name="All Cameras")
        for item in items:
            cam = Camera(
                id=item.get("id", ""),
                name=item.get("displayName", item.get("name", "")),
                device_id=item.get("id", ""),
                is_ptz=item.get("ptz", item.get("PTZ", False)),
                is_online=item.get("enabled", True),
                recording_server_id=item.get("relations", {}).get("parent", {}).get("id", ""),
                ip_address=item.get("address", ""),
                model=item.get("model", ""),
            )
            if cam.id:
                root.cameras.append(cam)
                self._cameras[cam.id] = cam
        return root

    def get_camera(self, camera_id: str) -> Camera | None:
        return self._cameras.get(camera_id)

    def all_cameras(self) -> list[Camera]:
        return list(self._cameras.values())

    def get_name(self, camera_id: str) -> str:
        cam = self._cameras.get(camera_id)
        return cam.name if cam else camera_id
