"""
REST API wrappers for Events
"""
from src.protocols.rest_api.client import RestClient


class EventsAPI:
    def __init__(self, client: RestClient):
        self._client = client

    async def get_events(self, limit: int = 100) -> list[dict]:
        resp = await self._client.get(f"/REST/v1/Events?$top={limit}")
        return resp.json()
