"""
WebSocket Event & State subscription

Reference: mipsdk-samples-protocol/EventsAndStateWebSocketApiPython
"""
import json
import asyncio
import websockets
from src.protocols.rest_api.client import RestClient


class EventStateWebSocket:
    """Subscribe to real-time events and state changes via WebSocket."""

    def __init__(self, rest_client: RestClient, server_url: str):
        self._rest = rest_client
        self._server_url = server_url.rstrip("/")
        self._ws = None
        self._running = False
        self._handlers: list[callable] = []

    def on_event(self, handler: callable):
        """Register an event handler: fn(event_data: dict)."""
        self._handlers.append(handler)

    async def connect(self):
        token = self._rest.auth.token
        ws_url = self._server_url.replace("https://", "wss://").replace(
            "http://", "ws://"
        )
        self._ws = await websockets.connect(
            f"{ws_url}/API/WS/EventsAndState?token={token}"
        )
        self._running = True
        asyncio.ensure_future(self._listen())

    async def _listen(self):
        while self._running and self._ws:
            try:
                msg = await self._ws.recv()
                data = json.loads(msg)
                for handler in self._handlers:
                    handler(data)
            except Exception:
                break

    async def disconnect(self):
        self._running = False
        if self._ws:
            await self._ws.close()
