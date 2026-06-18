"""
Session state — tracks connection to one VMS server
"""
from dataclasses import dataclass, field
from src.core.auth import AuthManager
from src.protocols.rest_api.client import RestClient
from src.protocols.mobile_xmlrpc.connection import MobileConnection


@dataclass
class ServerSession:
    """Holds all protocol clients for one VMS connection."""
    server_url: str
    api_gateway_url: str
    username: str
    auth: AuthManager = field(init=False)
    rest: RestClient = field(init=False)
    mobile: MobileConnection = field(init=False)
    connected: bool = False

    def __post_init__(self):
        self.auth = AuthManager(self.server_url, self.username, "")
        self.rest = RestClient(self.api_gateway_url, self.auth)
        self.mobile = MobileConnection(self.server_url)

    async def connect(self, password: str):
        self.auth.password = password
        self.auth.invalidate()
        _ = self.auth.token  # force initial token fetch
        self.connected = True

    async def disconnect(self):
        await self.mobile.disconnect()
        self.connected = False


class SessionManager:
    """Manages multiple server sessions (multi-site)."""
    _sessions: dict[str, ServerSession] = {}

    def get(self, name: str = "default") -> ServerSession:
        return self._sessions[name]

    def add(self, name: str, session: ServerSession):
        self._sessions[name] = session
