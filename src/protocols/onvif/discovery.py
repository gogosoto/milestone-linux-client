"""
ONVIF Camera Discovery — WS-Discovery + probe directly on Linux

Milestone's hardware scan is server-side. This implements
independent ONVIF discovery that can then add devices via the
REST Config API.
"""
import asyncio
import socket
import struct
import uuid
from xml.etree import ElementTree as ET

WS_DISCOVERY_MULTICAST_ADDR = "239.255.255.250"
WS_DISCOVERY_PORT = 3702

WS_DISCOVERY_PROBE = """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope
    xmlns:soap="http://www.w3.org/2003/05/soap-envelope"
    xmlns:wsa="http://schemas.xmlsoap.org/ws/2004/08/addressing"
    xmlns:wsd="http://schemas.xmlsoap.org/ws/2005/04/discovery"
    xmlns:dn="http://www.onvif.org/ver10/network/wsdl">
  <soap:Header>
    <wsa:Action>http://schemas.xmlsoap.org/ws/2005/04/discovery/Probe</wsa:Action>
    <wsa:MessageID>uuid:{message_id}</wsa:MessageID>
    <wsa:To>urn:schemas-xmlsoap-org:ws:2005:04:discovery</wsa:To>
  </soap:Header>
  <soap:Body>
    <wsd:Probe>
      <wsd:Types>dn:NetworkVideoTransmitter</wsd:Types>
    </wsd:Probe>
  </soap:Body>
</soap:Envelope>"""


class ONVIFDiscoveryResult:
    def __init__(self, address: str, xaddrs: str, types: str, scopes: str):
        self.address = address
        self.xaddrs = xaddrs
        self.types = types
        self.scopes = scopes
        self.model: str = ""
        self.manufacturer: str = ""

    def __repr__(self):
        return f"ONVIFDevice({self.address}, {self.xaddrs})"


async def discover_onvif_devices(timeout: float = 5.0) -> list[ONVIFDiscoveryResult]:
    """Send WS-Discovery Probe and collect responses."""
    devices = []

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.settimeout(timeout)

    # Set multicast TTL
    ttl = struct.pack("b", 4)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

    # Send probe
    probe_msg = WS_DISCOVERY_PROBE.format(message_id=str(uuid.uuid4()))
    sock.sendto(
        probe_msg.encode(),
        (WS_DISCOVERY_MULTICAST_ADDR, WS_DISCOVERY_PORT),
    )

    # Collect responses
    try:
        while True:
            data, addr = sock.recvfrom(65535)
            result = _parse_probe_match(data, addr)
            if result:
                devices.append(result)
    except socket.timeout:
        pass
    finally:
        sock.close()

    return devices


def _parse_probe_match(data: bytes, addr: tuple) -> ONVIFDiscoveryResult | None:
    """Parse a WS-Discovery ProbeMatch response."""
    try:
        root = ET.fromstring(data)
        ns = {
            "soap": "http://www.w3.org/2003/05/soap-envelope",
            "wsd": "http://schemas.xmlsoap.org/ws/2005/04/discovery",
            "wsa": "http://schemas.xmlsoap.org/ws/2004/08/addressing",
        }
        match = root.find(".//wsd:ProbeMatch", ns)
        if match is None:
            return None

        xaddrs_elem = match.find("wsd:XAddrs", ns)
        types_elem = match.find("wsd:Types", ns)
        scopes_elem = match.find("wsd:Scopes", ns)

        return ONVIFDiscoveryResult(
            address=f"{addr[0]}:{addr[1]}",
            xaddrs=xaddrs_elem.text if xaddrs_elem is not None else "",
            types=types_elem.text if types_elem is not None else "",
            scopes=scopes_elem.text if scopes_elem is not None else "",
        )
    except ET.ParseError:
        return None


async def get_device_info(xaddrs: str, username: str = "", password: str = "") -> dict:
    """Get ONVIF device information (model, manufacturer, firmware)."""
    try:
        from onvif import ONVIFCamera
        # Parse host from xaddrs
        from urllib.parse import urlparse
        parsed = urlparse(xaddrs.split(" ")[0])
        host = parsed.hostname
        port = parsed.port or 80

        camera = ONVIFCamera(host, port, username, password)
        device = camera.devicemgmt
        info = await device.GetDeviceInformation()
        return {
            "manufacturer": info.Manufacturer,
            "model": info.Model,
            "firmware": info.FirmwareVersion,
            "serial": info.SerialNumber,
        }
    except ImportError:
        return {"error": "onvif-zeep not installed. Run: pip install onvif-zeep"}
    except Exception as e:
        return {"error": str(e)}
