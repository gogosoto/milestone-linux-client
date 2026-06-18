"""
REST API wrappers for Config CRUD operations
"""
from src.protocols.rest_api.client import RestClient


class ConfigAPI:
    def __init__(self, client: RestClient):
        self._client = client

    async def get_cameras(self) -> list[dict]:
        resp = await self._client.get("/REST/v1/Config/Cameras")
        return resp.json()

    async def get_camera(self, camera_id: str) -> dict:
        resp = await self._client.get(f"/REST/v1/Config/Cameras('{camera_id}')")
        return resp.json()

    async def get_hardware(self) -> list[dict]:
        resp = await self._client.get("/REST/v1/Config/Hardware")
        return resp.json()

    async def get_recording_servers(self) -> list[dict]:
        resp = await self._client.get("/REST/v1/Config/RecordingServers")
        return resp.json()

    async def create_user_defined_event(self, name: str) -> dict:
        resp = await self._client.post(
            "/REST/v1/Config/UserDefinedEvents",
            json={"Name": name},
        )
        return resp.json()
