"""
gRPC bridge client — calls the Windows .NET shim for .NET-only features
"""
from pathlib import Path
import grpc
from grpc import aio

# Generated stubs — compile with:
#   python -m grpc_tools.protoc -I../proto --python_out=. --grpc_python_out=. ../proto/bridge.proto
from src.protocols.bridge import bridge_pb2, bridge_pb2_grpc


class BridgeClient:
    """Client for the Windows .NET bridge service."""

    def __init__(self, host: str = "localhost", port: int = 50051):
        self._address = f"{host}:{port}"
        self._channel: aio.Channel | None = None
        self._stub: bridge_pb2_grpc.MilestoneBridgeStub | None = None
        self.connected = False

    async def connect(self):
        self._channel = aio.insecure_channel(self._address)
        self._stub = bridge_pb2_grpc.MilestoneBridgeStub(self._channel)
        self.connected = True

    async def disconnect(self):
        if self._channel:
            await self._channel.close()
        self.connected = False

    # ── Smart Search ──────────────────────────────────────────────────

    async def start_motion_search(self, server_url: str, username: str,
                                  password: str, camera_id: str,
                                  start_time: float, end_time: float,
                                  roi: tuple[float, float, float, float] = (0, 0, 0, 0)
                                  ) -> dict:
        req = bridge_pb2.MotionSearchRequest(
            server_url=server_url, username=username, password=password,
            camera_id=camera_id, start_time=start_time, end_time=end_time,
            roi_x=roi[0], roi_y=roi[1], roi_w=roi[2], roi_h=roi[3],
        )
        resp = await self._stub.StartMotionSearch(req)
        return {"task_id": resp.task_id, "started": resp.started}

    async def get_motion_search_progress(self, task_id: str) -> dict:
        req = bridge_pb2.ProgressRequest(task_id=task_id)
        resp = await self._stub.GetMotionSearchProgress(req)
        return {
            "progress": resp.progress,
            "results": [
                {"timestamp": r.timestamp, "x": r.x, "y": r.y,
                 "w": r.w, "h": r.h, "confidence": r.confidence}
                for r in resp.results
            ],
        }

    # ── Evidence Lock ─────────────────────────────────────────────────

    async def lock_evidence(self, server_url: str, username: str,
                            password: str, camera_id: str,
                            start_time: float, end_time: float,
                            description: str = "") -> dict:
        req = bridge_pb2.EvidenceRequest(
            server_url=server_url, username=username, password=password,
            camera_id=camera_id, start_time=start_time, end_time=end_time,
            description=description,
        )
        resp = await self._stub.LockEvidence(req)
        return {"success": resp.success, "evidence_id": resp.evidence_id, "error": resp.error}

    async def unlock_evidence(self, **kw) -> dict:
        req = bridge_pb2.EvidenceRequest(**kw)
        resp = await self._stub.UnlockEvidence(req)
        return {"success": resp.success, "evidence_id": resp.evidence_id}

    async def get_locked_evidence(self, **kw) -> list[dict]:
        req = bridge_pb2.EvidenceListRequest(**kw)
        resp = await self._stub.GetLockedEvidence(req)
        return [
            {"id": i.id, "camera_id": i.camera_id, "description": i.description,
             "start_time": i.start_time, "end_time": i.end_time, "locked": i.locked}
            for i in resp.items
        ]

    # ── Hardware ──────────────────────────────────────────────────────

    async def scan_hardware(self, server_url: str, username: str,
                            password: str, ip_range: str,
                            recording_server_id: str) -> list[dict]:
        req = bridge_pb2.HardwareScanRequest(
            server_url=server_url, username=username, password=password,
            ip_range=ip_range, recording_server_id=recording_server_id,
        )
        resp = await self._stub.ScanHardware(req)
        return [
            {"ip": d.ip, "name": d.name, "manufacturer": d.manufacturer,
             "model": d.model, "driver": d.driver}
            for d in resp.devices
        ]

    async def add_hardware(self, **kw) -> dict:
        req = bridge_pb2.HardwareAddRequest(**kw)
        resp = await self._stub.AddHardware(req)
        return {"success": resp.success, "hardware_id": resp.hardware_id, "error": resp.error}

    async def remove_hardware(self, **kw) -> bool:
        req = bridge_pb2.HardwareRemoveRequest(**kw)
        resp = await self._stub.RemoveHardware(req)
        return True

    # ── System ────────────────────────────────────────────────────────

    async def get_system_logs(self, **kw) -> list[dict]:
        req = bridge_pb2.LogQuery(**kw)
        resp = await self._stub.GetSystemLogs(req)
        return [{"timestamp": e.timestamp, "level": e.level,
                 "source": e.source, "message": e.message} for e in resp.entries]

    async def get_system_status(self) -> dict:
        resp = await self._stub.GetSystemStatus(bridge_pb2.Empty())
        return {
            "status": resp.status, "cpu": resp.cpu_usage,
            "memory": resp.memory_usage, "disk": resp.disk_usage,
            "sessions": resp.active_sessions,
        }

    # ── Video Wall ────────────────────────────────────────────────────

    async def get_video_walls(self) -> list[dict]:
        resp = await self._stub.GetVideoWalls(bridge_pb2.Empty())
        return [{"id": w.id, "name": w.name, "width": w.width, "height": w.height}
                for w in resp.items]

    async def send_to_video_wall(self, **kw):
        req = bridge_pb2.VideoWallCommand(**kw)
        await self._stub.SendToVideoWall(req)

    # ── PTZ Patrols ───────────────────────────────────────────────────

    async def get_patrols(self, **kw) -> list[dict]:
        req = bridge_pb2.PatrolQuery(**kw)
        resp = await self._stub.GetPatrols(req)
        return [{"id": p.id, "name": p.name, "presets_count": p.presets_count}
                for p in resp.items]

    async def start_patrol(self, **kw):
        req = bridge_pb2.PatrolCommand(**kw)
        await self._stub.StartPatrol(req)

    async def stop_patrol(self, **kw):
        req = bridge_pb2.PatrolCommand(**kw)
        await self._stub.StopPatrol(req)
