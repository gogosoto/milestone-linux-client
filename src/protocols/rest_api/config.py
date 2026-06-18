"""
REST API wrappers for Config CRUD operations.
Milestone API Gateway uses flat resource paths:
  /api/REST/v1/Hardware  (not /Config/Hardware)
"""
from src.protocols.rest_api.client import RestClient


class ConfigAPI:
    def __init__(self, client: RestClient):
        self._client = client

    async def get_hardware(self) -> list[dict]:
        """Get all hardware (cameras, encoders, etc.)."""
        return await self._client.get_entities("Hardware")

    async def get_recording_servers(self) -> list[dict]:
        return await self._client.get_entities("RecordingServers")

    async def get_sites(self) -> list[dict]:
        return await self._client.get_entities("Sites")

    async def get_hardware_drivers(self) -> list[dict]:
        return await self._client.get_entities("HardwareDrivers")
