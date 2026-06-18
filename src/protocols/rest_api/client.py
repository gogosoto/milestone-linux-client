"""
Base REST API client for Milestone API Gateway

Handles authentication, token refresh, and the OData JSON format
used by Milestone's REST API.
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
        if "Content-Type" not in headers:
            headers["Content-Type"] = "application/json"

        resp = await self._client.request(method, url, headers=headers, **kwargs)
        if resp.status_code == 401:
            self.auth.invalidate()
            headers["Authorization"] = f"Bearer {self.auth.token}"
            resp = await self._client.request(method, url, headers=headers, **kwargs)
        resp.raise_for_status()
        return resp

    async def get_entities(self, resource: str, **params) -> list[dict]:
        """Get all entities of a resource, handling next page links."""
        items = []
        path = f"/api/REST/v1/{resource}"
        while path:
            resp = await self.get(path, params=params)
            data = resp.json()
            items.extend(data.get("array", data.get("value", [])))
            links = data.get("_links", {})
            path = links.get("next", {}).get("href") if isinstance(links, dict) else None
        return items

    async def close(self):
        await self._client.aclose()
