"""
REST API wrapper for WebRTC session lifecycle

If the API Gateway doesn't have the WebRTC module installed,
this will fail with 400/404 and video falls back to bridge.
"""
from src.protocols.rest_api.client import RestClient


class WebRTCRestClient:
    def __init__(self, client: RestClient):
        self._client = client

    async def create_session(
        self,
        device_id: str,
        *,
        stream_id: str | None = None,
        include_audio: bool = True,
        playback_time: str | None = None,
        speed: float | None = None,
        skip_gaps: bool = False,
        ice_servers: list[dict] | None = None,
    ) -> dict:
        body = {"deviceId": device_id, "resolution": "notInUse", "includeAudio": include_audio}
        if stream_id:
            body["streamId"] = stream_id
        if playback_time:
            pt_node = {"playbackTime": playback_time}
            if speed:
                pt_node["speed"] = speed
            pt_node["skipGaps"] = skip_gaps
            body["playbackTimeNode"] = pt_node
        if ice_servers:
            body["iceServers"] = ice_servers

        resp = await self._client.post("/api/REST/v1/WebRTC/Session", json=body)
        return resp.json()

    async def update_answer_sdp(self, session_id: str, answer_sdp: str) -> dict:
        resp = await self._client.patch(
            f"/api/REST/v1/WebRTC/Session('{session_id}')",
            json={"answerSDP": answer_sdp},
        )
        return resp.json()

    async def get_ice_candidates(self, session_id: str) -> list[dict]:
        resp = await self._client.get(f"/api/REST/v1/WebRTC/IceCandidates('{session_id}')")
        return resp.json()

    async def send_ice_candidates(self, session_id: str, candidates: list[str]):
        await self._client.post(
            f"/api/REST/v1/WebRTC/IceCandidates('{session_id}')",
            json={"candidates": candidates},
        )
