"""
Camera service — fetches camera list via REST Config API, builds tree
"""
from src.protocols.rest_api.config import ConfigAPI
from src.protocols.mobile_xmlrpc.connection import MobileConnection
from src.models import Camera, CameraGroup


class CameraService:
    def __init__(self, mobile: MobileConnection, config: ConfigAPI):
        self._mobile = mobile
        self._config = config
        self._cameras: dict[str, Camera] = {}

    async def refresh(self) -> CameraGroup:
        """Fetch all cameras from the REST Config API."""
        raw = await self._config.get_cameras()
        # REST Config API returns different formats depending on server version
        items = raw.get("value", raw if isinstance(raw, list) else [])
        root = CameraGroup(id="root", name="All Cameras")
        for item in items:
            cam = Camera(
                id=item.get("ItemId", item.get("Id", "")),
                name=item.get("DisplayName", item.get("Name", "")),
                device_id=item.get("DeviceId", item.get("Id", "")),
                is_ptz=item.get("PTZ", False),
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
