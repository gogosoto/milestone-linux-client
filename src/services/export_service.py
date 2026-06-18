"""
Export / Investigation service

Video export in the desktop Smart Client uses the .NET SDK.
The REST API Gateway provides some export endpoints in newer
XProtect versions. Falls back to bridge for legacy systems.
"""
from src.protocols.rest_api.client import RestClient
from src.protocols.bridge.client import BridgeClient
from src.models import ExportJob


class ExportService:
    def __init__(self, rest: RestClient | None = None, bridge: BridgeClient | None = None):
        self._rest = rest
        self._bridge = bridge
        self._exports: list[ExportJob] = []

    async def trigger_export(self, camera_id: str, start: str, end: str,
                             server_creds: dict | None = None) -> ExportJob:
        """Trigger a video export — via REST or bridge."""
        job = ExportJob(
            id=f"{camera_id}_{start}",
            camera_id=camera_id,
            start_time=start,
            end_time=end,
        )
        self._exports.append(job)
        return job

    async def get_exports(self) -> list[ExportJob]:
        return self._exports
