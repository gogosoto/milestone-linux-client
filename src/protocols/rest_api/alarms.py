"""
REST API wrappers for Alarms CRUD
"""
from src.protocols.rest_api.client import RestClient


class AlarmsAPI:
    def __init__(self, client: RestClient):
        self._client = client

    async def list_alarms(self, limit: int = 100, offset: int = 0) -> list[dict]:
        resp = await self._client.get(f"/REST/v1/Alarms?$top={limit}&$skip={offset}")
        return resp.json()

    async def get_alarm(self, alarm_id: str) -> dict:
        resp = await self._client.get(f"/REST/v1/Alarms('{alarm_id}')")
        return resp.json()

    async def acknowledge_alarm(self, alarm_id: str):
        resp = await self._client.patch(
            f"/REST/v1/Alarms('{alarm_id}')",
            json=[{"op": "replace", "path": "/Acknowledged", "value": True}],
        )
        return resp.json()
