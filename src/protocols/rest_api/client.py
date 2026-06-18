"""
Base REST API client for the API Gateway
"""
import httpx
from src.core.auth import AuthManager


class RestClient:
    """Async HTTP client for Milestone API Gateway REST endpoints."""

    def __init__(self, base_url: str, auth: AuthManager):
        self.base_url = base_url.rstrip("/")
        self.auth = auth
        self._client = httpx.AsyncClient(verify=False, timeout=30.0)

    async def get(self, path: str, **kwargs) -> httpx.Response:
        return await self._request("GET", path, **kwargs)

    async def post(self, path: str, **kwargs) -> httpx.Response:
        return await self._request("POST", path, **kwargs)

    async def patch(self, path: str, **kwargs) -> httpx.Response:
        return await self._request("PATCH", path, **kwargs)

    async def delete(self, path: str, **kwargs) -> httpx.Response:
        return await self._request("DELETE", path, **kwargs)

    async def _request(self, method: str, path: str, **kwargs) -> httpx.Response:
        url = f"{self.base_url}{path}"
        headers = kwargs.pop("headers", {})
        headers.setdefault("Authorization", f"Bearer {self.auth.token}")
        headers.setdefault("Content-Type", "application/json")

        resp = await self._client.request(method, url, headers=headers, **kwargs)
        if resp.status_code == 401:
            self.auth.invalidate()
            headers["Authorization"] = f"Bearer {self.auth.token}"
            resp = await self._client.request(method, url, headers=headers, **kwargs)
        resp.raise_for_status()
        return resp

    async def close(self):
        await self._client.aclose()
