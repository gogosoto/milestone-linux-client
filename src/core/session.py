"""
ServerSession — holds all protocol clients for one XProtect VMS connection.

Desktop Smart Client uses:
  - REST API Gateway (management, config, alarms, events, WebRTC)
  - WebRTC (live/playback video, PTZ)
  - gRPC Bridge → Windows .NET SDK (Smart Search, hardware mgmt, etc.)
"""
from dataclasses import dataclass, field
from src.core.auth import AuthManager
from src.protocols.rest_api.client import RestClient
from src.protocols.rest_api.webrtc import WebRTCRestClient
from src.protocols.rest_api.config import ConfigAPI
from src.protocols.rest_api.alarms import AlarmsAPI
from src.protocols.rest_api.bookmarks import BookmarksAPI
from src.protocols.rest_api.events import EventsAPI
from src.protocols.webrtc.session_manager import WebRTCSessionManager
from src.protocols.bridge.client import BridgeClient


@dataclass
class ServerSession:
    """One authenticated connection to a Milestone XProtect VMS server."""
    server_url: str
    api_gateway_url: str
    username: str
    bridge_host: str = ""
    bridge_port: int = 0

    auth: AuthManager = field(init=False)
    rest: RestClient = field(init=False)
    webrtc: WebRTCRestClient = field(init=False)
    config_api: ConfigAPI = field(init=False)
    alarms: AlarmsAPI = field(init=False)
    bookmarks: BookmarksAPI = field(init=False)
    events: EventsAPI = field(init=False)
    webrtc_manager: WebRTCSessionManager = field(init=False)
    bridge: BridgeClient | None = field(init=False)
    connected: bool = False

    def __post_init__(self):
        self.auth = AuthManager(self.server_url, self.username, "")
        self.rest = RestClient(self.api_gateway_url or self.server_url, self.auth)
        self.webrtc = WebRTCRestClient(self.rest)
        self.config_api = ConfigAPI(self.rest)
        self.alarms = AlarmsAPI(self.rest)
        self.bookmarks = BookmarksAPI(self.rest)
        self.events = EventsAPI(self.rest)
        self.webrtc_manager = WebRTCSessionManager(self.webrtc)

        if self.bridge_host:
            self.bridge = BridgeClient(self.bridge_host, self.bridge_port)
        else:
            self.bridge = None

    async def connect(self, password: str):
        """Authenticate with OAuth2 and connect bridge."""
        self.auth.password = password
        _ = self.auth.token  # force token fetch
        if self.bridge:
            await self.bridge.connect()
        self.connected = True

    async def disconnect(self):
        await self.webrtc_manager.stop_all()
        if self.bridge:
            await self.bridge.disconnect()
        self.connected = False


class SessionManager:
    """Multi-server session registry."""
    _sessions: dict[str, ServerSession] = {}

    def get(self, name: str = "default") -> ServerSession | None:
        return self._sessions.get(name)

    def add(self, name: str, session: ServerSession):
        self._sessions[name] = session
