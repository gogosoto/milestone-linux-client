"""
XProtect Mobile XML-RPC Protocol — Connection Lifecycle

Manages the full connection lifecycle: Connect → DH exchange → Login → commands.

Reference: XPMobileSDK.js/Lib/Connection.js
"""
import httpx
from src.protocols.mobile_xmlrpc.auth import MobileAuth
from src.protocols.mobile_xmlrpc.commands import (
    build_connect, build_login, build_get_all_views,
    build_request_stream, build_change_stream, build_close_stream,
    build_get_next_sequence, build_get_prev_sequence,
    build_carousel_next, build_carousel_prev, build_carousel_pause, build_carousel_resume,
    build_get_thumbnail, build_create_playback_controller, build_trigger_export,
    build_audio_push,
)
from src.protocols.mobile_xmlrpc.parser import (
    parse_connect_response, parse_login_response, parse_device_list,
)


class MobileConnection:
    """Manages a single Mobile SDK XML-RPC connection to an XProtect server."""

    def __init__(self, server_url: str):
        self.server_url = server_url.rstrip("/")
        self._client = httpx.AsyncClient(verify=False, timeout=30.0)
        self._auth = MobileAuth()
        self._connection_id: str | None = None
        self._sequence_id: int = 0
        self.connected: bool = False

    async def connect(self, username: str, password: str):
        """Full connection + login flow."""
        # Step 1: Connect — get DH params + challenge
        resp1 = await self._call(build_connect())
        conn_info = parse_connect_response(resp1)
        self._connection_id = conn_info["connection_id"]

        # Step 2: DH key exchange
        client_pub, _ = self._auth.generate_client_key_pair()
        server_pub = int(conn_info["server_public_key"])
        self._auth.compute_shared_secret(server_pub)

        # Step 3: Login with CHAP response
        chap_response = self._auth.compute_chap_response(
            password, conn_info["challenge"]
        )
        resp2 = await self._call(
            build_login(username, chap_response, conn_info["session_key"],
                       self._connection_id)
        )
        login_info = parse_login_response(resp2)
        if not login_info["success"]:
            raise ConnectionError(f"Mobile login failed: {login_info['error']}")
        self.connected = True

    async def disconnect(self):
        self.connected = False
        await self._client.aclose()

    async def get_all_views(self) -> list[dict]:
        """Get camera tree."""
        resp = await self._call(build_get_all_views(self._connection_id))
        return parse_device_list(resp)

    async def request_stream(self, device_id: str, stream_type: str = "live") -> dict:
        """Request a video stream URL."""
        resp = await self._call(
            build_request_stream(self._connection_id, device_id, stream_type)
        )
        from src.protocols.mobile_xmlrpc.parser import parse_stream_response
        return parse_stream_response(resp)

    async def change_stream(self, device_id: str):
        """Switch stream to a different device (sequences)."""
        await self._call(build_change_stream(self._connection_id, device_id))

    async def close_stream(self, device_id: str):
        await self._call(build_close_stream(self._connection_id, device_id))

    async def get_next_sequence(self, view_id: str) -> dict:
        resp = await self._call(
            build_get_next_sequence(self._connection_id, view_id)
        )
        from src.protocols.mobile_xmlrpc.parser import MobileResponse
        r = MobileResponse(resp)
        return {"device_id": r.get("DeviceId"), "name": r.get("DisplayName")}

    async def get_prev_sequence(self, view_id: str) -> dict:
        resp = await self._call(
            build_get_prev_sequence(self._connection_id, view_id)
        )
        from src.protocols.mobile_xmlrpc.parser import MobileResponse
        r = MobileResponse(resp)
        return {"device_id": r.get("DeviceId"), "name": r.get("DisplayName")}

    async def carousel_next(self):
        await self._call(build_carousel_next(self._connection_id))

    async def carousel_prev(self):
        await self._call(build_carousel_prev(self._connection_id))

    async def carousel_pause(self):
        await self._call(build_carousel_pause(self._connection_id))

    async def carousel_resume(self):
        await self._call(build_carousel_resume(self._connection_id))

    async def get_thumbnail(self, device_id: str, time: str,
                            width: int = 320, height: int = 240) -> bytes:
        """Get thumbnail image data."""
        resp = await self._call(
            build_get_thumbnail(self._connection_id, device_id, time, width, height)
        )
        # Thumbnails come back as base64-encoded in the response
        from src.protocols.mobile_xmlrpc.parser import MobileResponse
        r = MobileResponse(resp)
        import base64
        return base64.b64decode(r.get("ImageData", ""))

    async def create_playback_controller(self, device_id: str, start_time: str):
        await self._call(
            build_create_playback_controller(self._connection_id, device_id, start_time)
        )

    async def trigger_export(self, device_id: str, start_time: str, end_time: str):
        await self._call(
            build_trigger_export(self._connection_id, device_id, start_time, end_time)
        )

    async def create_audio_push(self, device_id: str) -> str:
        """Get audio push URL for two-way audio."""
        resp = await self._call(
            build_audio_push(self._connection_id, device_id)
        )
        from src.protocols.mobile_xmlrpc.parser import MobileResponse
        r = MobileResponse(resp)
        return r.get("AudioPushUrl", "")

    async def _call(self, xml_request: str) -> str:
        """Send an XML-RPC request to the Mobile protocol endpoint."""
        self._sequence_id += 1
        resp = await self._client.post(
            f"{self.server_url}/XProtectMobile/Communication",
            content=xml_request,
            headers={"Content-Type": "text/xml"},
        )
        resp.raise_for_status()
        return resp.text
