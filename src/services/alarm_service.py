"""
Alarm service — alarm list, acknowledge, subscription
"""
from src.protocols.rest_api.alarms import AlarmsAPI
from src.protocols.websocket_events.client import EventStateWebSocket
from src.models import Alarm


class AlarmService:
    def __init__(self, alarms_api: AlarmsAPI, ws_events: EventStateWebSocket):
        self._api = alarms_api
        self._ws = ws_events
        self._alarms: list[Alarm] = []
        self._ws.on_event(self._on_event)

    async def refresh(self):
        data = await self._api.list_alarms()
        self._alarms = []
        for item in data:
            self._alarms.append(Alarm(
                id=item.get("Id", ""),
                name=item.get("DisplayName", item.get("Name", "")),
                priority=item.get("Priority", 0),
                state=item.get("State", "New"),
                camera_id=item.get("CameraId", ""),
                camera_name=item.get("CameraName", ""),
                description=item.get("Description", ""),
            ))
        return self._alarms

    async def acknowledge(self, alarm_id: str):
        await self._api.acknowledge_alarm(alarm_id)
        for a in self._alarms:
            if a.id == alarm_id:
                a.state = "Acknowledged"
                break

    def _on_event(self, event_data: dict):
        """Handle real-time alarm events from WebSocket."""
        # Parse and append new alarms as they arrive
        pass

    @property
    def alarms(self) -> list[Alarm]:
        return self._alarms

    @property
    def unacknowledged_count(self) -> int:
        return sum(1 for a in self._alarms if a.state == "New")
