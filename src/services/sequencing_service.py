"""
Sequencing / Tour service
"""
from src.protocols.mobile_xmlrpc.connection import MobileConnection


class SequencingService:
    def __init__(self, mobile: MobileConnection):
        self._mobile = mobile
        self._active_sequence_id: str | None = None
        self._is_carousel: bool = False

    async def next_in_sequence(self, view_id: str) -> dict:
        result = await self._mobile.get_next_sequence(view_id)
        return result

    async def prev_in_sequence(self, view_id: str) -> dict:
        result = await self._mobile.get_prev_sequence(view_id)
        return result

    async def carousel_next(self):
        await self._mobile.carousel_next()

    async def carousel_prev(self):
        await self._mobile.carousel_prev()

    async def carousel_pause(self):
        await self._mobile.carousel_pause()

    async def carousel_resume(self):
        await self._mobile.carousel_resume()
