"""
ServerSession — holds all protocol clients for one XProtect VMS connection.
"""
from dataclasses import dataclass, field
from src.core.auth import AuthManager
from src.protocols.rest_api.client import RestClient
from src.protocols.rest_api.webrtc import WebRTCRestClient
from src.protocols.rest_api.config import ConfigAPI
from src.protocols.rest_api.alarms import AlarmsAPI
from src.protocols.rest_api.bookmarks import BookmarksAPI
from src.protocols.rest_api.events import EventsAPI
from src.protocols.mobile_xmlrpc.connection import MobileConnection
from src.protocols.webrtc.session_manager import WebRTCSessionManager


@dataclass
class ServerSession:
    """One authenticated connection to a Milestone XProtect VMS server."""
    server_url: str
    api_gateway_url: str
    username: str
    auth: AuthManager = field(init=False)
    rest: RestClient = field(init=False)
    webrtc: WebRTCRestClient = field(init=False)
    config_api: ConfigAPI = field(init=False)
    alarms: AlarmsAPI = field(init=False)
    bookmarks: BookmarksAPI = field(init=False)
    events: EventsAPI = field(init=False)
    mobile: MobileConnection = field(init=False)
    webrtc_manager: WebRTCSessionManager = field(init=False)
    connected: bool = False

    def __post_init__(self):
        self.auth = AuthManager(self.server_url, self.username, "")
        self.rest = RestClient(self.api_gateway_url or self.server_url, self.auth)
        self.webrtc = WebRTCRestClient(self.rest)
        self.config_api = ConfigAPI(self.rest)
        self.alarms = AlarmsAPI(self.rest)
        self.bookmarks = BookmarksAPI(self.rest)
        self.events = EventsAPI(self.rest)
        self.mobile = MobileConnection(self.server_url)
        self.webrtc_manager = WebRTCSessionManager(self.webrtc)

    async def connect(self, password: str):
        """Authenticate with both REST (OAuth2) and Mobile (DH+CHAP)."""
        self.auth.password = password
        _ = self.auth.token  # force OAuth2 token fetch
        await self.mobile.connect(self.username, password)
        self.connected = True

    async def disconnect(self):
        await self.webrtc_manager.stop_all()
        await self.mobile.disconnect()
        self.connected = False


class SessionManager:
    """Multi-server session registry."""
    _sessions: dict[str, ServerSession] = {}

    def get(self, name: str = "default") -> ServerSession | None:
        return self._sessions.get(name)

    def add(self, name: str, session: ServerSession):
        self._sessions[name] = session
