"""
Sequencing / Tour service

In the desktop Smart Client, sequences and tours are managed
through the .NET SDK (via bridge) or configured on the server.
A basic tour cycles through cameras in a view.

For Phase 1, this is a placeholder — sequenced views are a
. NET SDK feature. The Linux client will implement camera cycling
at the UI level by changing which camera each grid slot shows.
"""
from src.protocols.bridge.client import BridgeClient


class SequencingService:
    def __init__(self, bridge: BridgeClient | None = None):
        self._bridge = bridge
        self._active = False
        self._timer_interval = 10  # seconds

    async def start_sequence(self, camera_ids: list[str]):
        """Cycle through cameras at interval — implemented client-side."""
        self._active = True
        self._camera_ids = camera_ids
        self._current_index = 0

    async def stop_sequence(self):
        self._active = False

    @property
    def is_active(self) -> bool:
        return self._active
