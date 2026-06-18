"""
XProtect Mobile XML-RPC Protocol — XML Command Builder

Builds the XML request payloads for the Mobile SDK protocol.

Reference: XPMobileSDK.js/Lib/ConnectionRequest.js
"""
import xml.etree.ElementTree as ET
import uuid


def _make_command(name: str, params: list[tuple[str, str]] | None = None,
                  connection_id: str | None = None, sequence_id: int = 1) -> str:
    """Build the standard XML command envelope."""
    comm = ET.Element("Communication")
    if connection_id:
        conn_id = ET.SubElement(comm, "ConnectionId")
        conn_id.text = connection_id
    cmd = ET.SubElement(comm, "Command")
    cmd.set("SequenceId", str(sequence_id))
    cmd_type = ET.SubElement(cmd, "Type")
    cmd_type.text = "Request"
    cmd_name = ET.SubElement(cmd, "Name")
    cmd_name.text = name
    if params:
        inp = ET.SubElement(cmd, "InputParams")
        for key, value in params:
            p = ET.SubElement(inp, "Param")
            p.set("Name", key)
            p.set("Value", value)
    return ET.tostring(comm, encoding="unicode", xml_declaration=True)


def build_connect(server_id: str = "default") -> str:
    """Initial connection — server responds with DH params + challenge."""
    return _make_command("Connect", [
        ("ServerId", server_id),
        ("ClientType", "Desktop"),
        ("ClientVersion", "1.0.0"),
    ])


def build_login(username: str, password_encrypted: str, session_key: str,
                connection_id: str) -> str:
    """Login with encrypted password and challenge response."""
    return _make_command("LogIn", [
        ("UserName", username),
        ("Password", password_encrypted),
        ("SessionKey", session_key),
        ("ClientType", "Desktop"),
        ("Language", "en"),
    ], connection_id=connection_id)


def build_get_all_views(connection_id: str) -> str:
    """Get the camera tree / all views."""
    return _make_command("GetAllViews", connection_id=connection_id)


def build_request_stream(connection_id: str, device_id: str,
                         stream_type: str = "live") -> str:
    """Request a video stream for a device."""
    params = [("DeviceId", device_id), ("StreamType", stream_type)]
    return _make_command("RequestStream", params, connection_id=connection_id)


def build_change_stream(connection_id: str, device_id: str) -> str:
    """Switch an existing stream to a different device (sequences/carousel)."""
    return _make_command("ChangeStream", [("DeviceId", device_id)],
                         connection_id=connection_id)


def build_close_stream(connection_id: str, device_id: str) -> str:
    """Close a video stream."""
    return _make_command("CloseStream", [("DeviceId", device_id)],
                         connection_id=connection_id)


def build_get_next_sequence(connection_id: str, view_id: str) -> str:
    """Get the next camera in a sequence/tour."""
    return _make_command("GetNextSequence", [("ViewId", view_id)],
                         connection_id=connection_id)


def build_get_prev_sequence(connection_id: str, view_id: str) -> str:
    """Get the previous camera in a sequence/tour."""
    return _make_command("GetPrevSequence", [("ViewId", view_id)],
                         connection_id=connection_id)


def build_carousel_next(connection_id: str) -> str:
    """Switch to next camera in carousel mode."""
    return _make_command("CarouselNextCamera", connection_id=connection_id)


def build_carousel_prev(connection_id: str) -> str:
    """Switch to previous camera in carousel mode."""
    return _make_command("CarouselPrevCamera", connection_id=connection_id)


def build_carousel_pause(connection_id: str) -> str:
    return _make_command("CarouselPause", connection_id=connection_id)


def build_carousel_resume(connection_id: str) -> str:
    return _make_command("CarouselResume", connection_id=connection_id)


def build_get_thumbnail(connection_id: str, device_id: str,
                        time: str, width: int = 320, height: int = 240) -> str:
    """Get a thumbnail frame at a specific time."""
    return _make_command("GetThumbnailByTime", [
        ("DeviceId", device_id),
        ("Time", time),
        ("Width", str(width)),
        ("Height", str(height)),
    ], connection_id=connection_id)


def build_create_playback_controller(connection_id: str, device_id: str,
                                     start_time: str) -> str:
    """Create a playback session for a device."""
    return _make_command("CreatePlaybackController", [
        ("DeviceId", device_id),
        ("StartTime", start_time),
    ], connection_id=connection_id)


def build_trigger_export(connection_id: str, device_id: str,
                         start_time: str, end_time: str) -> str:
    """Trigger an investigation export."""
    return _make_command("TriggerInvestigationExport", [
        ("DeviceId", device_id),
        ("StartTime", start_time),
        ("EndTime", end_time),
    ], connection_id=connection_id)


def build_audio_push(connection_id: str, device_id: str) -> str:
    """Create a two-way audio push connection."""
    return _make_command("CreateAudioPushConnection", [
        ("DeviceId", device_id),
    ], connection_id=connection_id)
