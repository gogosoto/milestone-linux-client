"""
OAuth2 / OIDC authentication with token refresh
"""
import time
import httpx


class AuthManager:
    """Manages OAuth2 bearer tokens for the API Gateway."""

    def __init__(self, server_url: str, username: str, password: str, auth_type: str = "basic"):
        self.server_url = server_url.rstrip("/")
        self.username = username
        self.password = password
        self.auth_type = auth_type
        self._token: str | None = None
        self._expires_at: float = 0
        self._client = httpx.Client(verify=False)  # TODO: proper TLS in production

    @property
    def token(self) -> str:
        if not self._token or time.time() > self._expires_at - 60:
            self._refresh_token()
        return self._token

    def _refresh_token(self):
        if self.auth_type == "basic":
            resp = self._client.post(
                f"{self.server_url}/API/IDP/connect/token",
                data={
                    "grant_type": "password",
                    "username": self.username,
                    "password": self.password,
                    "client_id": "GrantValidatorClient",
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
        else:
            # Windows NTLM auth — goes directly to IDP
            from requests_ntlm import HttpNtlmAuth  # optional dep
            resp = self._client.post(
                f"{self.server_url}/IDP/connect/token",
                data={
                    "grant_type": "windows_credentials",
                    "client_id": "GrantValidatorClient",
                },
                auth=HttpNtlmAuth(self.username, self.password),
            )

        resp.raise_for_status()
        data = resp.json()
        self._token = data["access_token"]
        self._expires_at = time.time() + data.get("expires_in", 3600)

    def invalidate(self):
        self._token = None
        self._expires_at = 0
