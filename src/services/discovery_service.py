"""
ONVIF discovery service — find cameras on the network
"""
from src.protocols.onvif.discovery import discover_onvif_devices, get_device_info
from src.protocols.bridge.client import BridgeClient


class DiscoveryService:
    def __init__(self, bridge: BridgeClient | None = None):
        self._bridge = bridge

    async def discover(self, timeout: float = 5.0) -> list[dict]:
        """Discover ONVIF cameras on the local network."""
        devices = await discover_onvif_devices(timeout)
        results = []
        for d in devices:
            info = await get_device_info(d.xaddrs)
            results.append({
                "address": d.address,
                "xaddrs": d.xaddrs,
                "manufacturer": info.get("manufacturer", ""),
                "model": info.get("model", ""),
                "firmware": info.get("firmware", ""),
            })
        return results

    async def add_to_vms(self, server_creds: dict, **hardware_params) -> dict:
        """Add discovered device to Milestone via bridge."""
        if self._bridge:
            return await self._bridge.add_hardware(**server_creds, **hardware_params)
        return {"success": False, "error": "Bridge not connected"}
