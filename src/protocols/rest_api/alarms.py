"""
REST API wrappers for Alarms CRUD
"""
from src.protocols.rest_api.client import RestClient


class AlarmsAPI:
    def __init__(self, client: RestClient):
        self._client = client

    async def list_alarms(self, limit: int = 100, offset: int = 0) -> list[dict]:
        return await self._client.get_entities(
            "Alarms", params={"$top": limit, "$skip": offset}
        )
