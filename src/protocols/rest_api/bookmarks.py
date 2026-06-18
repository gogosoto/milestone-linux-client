"""
REST API wrappers for Bookmarks CRUD
"""
from src.protocols.rest_api.client import RestClient


class BookmarksAPI:
    def __init__(self, client: RestClient):
        self._client = client

    async def list_bookmarks(self, camera_id: str | None = None) -> list[dict]:
        path = "/REST/v1/Bookmarks"
        if camera_id:
            path += f"?cameraId={camera_id}"
        resp = await self._client.get(path)
        return resp.json()

    async def create_bookmark(
        self, camera_id: str, time: str, description: str = ""
    ) -> dict:
        resp = await self._client.post(
            "/REST/v1/Bookmarks",
            json={
                "CameraId": camera_id,
                "Time": time,
                "Description": description,
            },
        )
        return resp.json()

    async def delete_bookmark(self, bookmark_id: str):
        await self._client.delete(f"/REST/v1/Bookmarks('{bookmark_id}')")
