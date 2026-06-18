"""
REST API wrappers for Bookmarks CRUD
"""
from src.protocols.rest_api.client import RestClient


class BookmarksAPI:
    def __init__(self, client: RestClient):
        self._client = client

    async def list_bookmarks(self, camera_id: str | None = None) -> list[dict]:
        params = {}
        if camera_id:
            params["cameraId"] = camera_id
        return await self._client.get_entities("Bookmarks", params=params)

    async def create_bookmark(
        self, camera_id: str, time: str, description: str = ""
    ) -> dict:
        resp = await self._client.post(
            "/api/REST/v1/Bookmarks",
            json={"CameraId": camera_id, "Time": time, "Description": description},
        )
        return resp.json()
