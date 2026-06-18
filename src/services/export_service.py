"""
Export / Investigation service
"""
from src.protocols.mobile_xmlrpc.connection import MobileConnection
from src.models import ExportJob


class ExportService:
    def __init__(self, mobile: MobileConnection):
        self._mobile = mobile
        self._exports: list[ExportJob] = []

    async def trigger_export(self, camera_id: str, start: str, end: str) -> ExportJob:
        await self._mobile.trigger_export(camera_id, start, end)
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
