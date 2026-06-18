"""
XProtect Mobile XML-RPC Protocol — Response Parser

Parses the XML response from the Mobile protocol.

Reference: XPMobileSDK.js/Lib/ConnectionResponse.js
"""
import xml.etree.ElementTree as ET


class MobileResponse:
    """Parsed response from a Mobile XML-RPC call."""

    def __init__(self, xml_data: str):
        self.root = ET.fromstring(xml_data)
        self._parse()

    def _parse(self):
        self.success = self.root.findtext(".//Result", "false") == "true"
        self.error = self.root.findtext(".//ErrorString", "")
        self.connection_id = self.root.findtext("ConnectionId", "")
        self.params: dict[str, str] = {}

        params_elem = self.root.find(".//OutputParams")
        if params_elem is not None:
            for param in params_elem.findall("Param"):
                name = param.get("Name", "")
                value = param.get("Value", "")
                self.params[name] = value

    def get(self, key: str, default: str = "") -> str:
        return self.params.get(key, default)


def parse_connect_response(xml_data: str) -> dict:
    """Extract DH params and challenge from Connect response."""
    resp = MobileResponse(xml_data)
    return {
        "connection_id": resp.connection_id,
        "dh_prime": resp.get("DHPrime"),
        "dh_generator": resp.get("DHGenerator"),
        "server_public_key": resp.get("ServerPublicKey"),
        "challenge": resp.get("Challenge"),
        "session_key": resp.get("SessionKey"),
    }


def parse_login_response(xml_data: str) -> dict:
    resp = MobileResponse(xml_data)
    return {
        "success": resp.success,
        "connection_id": resp.connection_id,
        "error": resp.error,
    }


def parse_device_list(xml_data: str) -> list[dict]:
    """Parse GetAllViews response into a device tree."""
    resp = MobileResponse(xml_data)
    devices = []
    for device_elem in resp.root.findall(".//Device"):
        devices.append({
            "id": device_elem.get("Id", ""),
            "name": device_elem.get("DisplayName", ""),
            "type": device_elem.get("DeviceType", ""),
            "parent_id": device_elem.get("ParentId", ""),
        })
    return devices


def parse_stream_response(xml_data: str) -> dict:
    resp = MobileResponse(xml_data)
    return {
        "video_url": resp.get("VideoUrl"),
        "stream_id": resp.get("StreamId"),
        "success": resp.success,
    }
