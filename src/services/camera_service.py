"""
Camera service — manages camera tree, state, grouping
"""
from src.protocols.mobile_xmlrpc.connection import MobileConnection
from src.models import Camera, CameraGroup


class CameraService:
    def __init__(self, mobile: MobileConnection):
        self._mobile = mobile
        self._root_group = CameraGroup(id="root", name="All Cameras")
        self._cameras: dict[str, Camera] = {}

    async def refresh(self):
        """Fetch camera tree from server."""
        devices = await self._mobile.get_all_views()
        cameras = []
        groups = {}
        for d in devices:
            if d["type"] == "Camera":
                cam = Camera(
                    id=d["id"],
                    name=d["name"],
                    device_id=d["id"],
                    group_id=d.get("parent_id", ""),
                )
                cameras.append(cam)
                self._cameras[cam.id] = cam
            elif d["type"] == "Group":
                groups[d["id"]] = d["name"]

        # Build hierarchy
        self._root_group = CameraGroup(id="root", name="All Cameras")
        for cam in cameras:
            self._root_group.cameras.append(cam)
        return self._root_group

    def get_camera(self, camera_id: str) -> Camera | None:
        return self._cameras.get(camera_id)

    def all_cameras(self) -> list[Camera]:
        return list(self._cameras.values())

    def get_name(self, camera_id: str) -> str:
        cam = self._cameras.get(camera_id)
        return cam.name if cam else camera_id
