"""
ImageServer TCP Protocol — live/playback video streaming

The Smart Client connects directly to the Recording Server's ImageServer
on port 7563 using a simple XML-over-TCP protocol. The server streams
JPEG frames in return.

Reference: mipsdk-samples-protocol/TcpVideoViewer/ImageServerConnection.cs
"""
import asyncio
import socket
import ssl
import xml.etree.ElementTree as ET
from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QImage


class ImageServerClient(QObject):
    """TCP client for Milestone ImageServer video streaming."""

    frame_received = Signal(str, object)  # camera_id, QImage
    connection_state = Signal(str, str)   # camera_id, state

    def __init__(self, host: str, port: int = 7563, use_ssl: bool = False):
        super().__init__()
        self._host = host
        self._port = port
        self._use_ssl = use_ssl
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._camera_id: str = ""
        self._running = False
        self._req_counter = 0

    async def connect_live(self, camera_id: str, token: str):
        """Connect to ImageServer and start live video stream."""
        self._camera_id = camera_id
        self._running = True

        # TCP connect
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((self._host, self._port))

            if self._use_ssl:
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                sock = ctx.wrap_socket(sock, server_hostname=self._host)

            self._reader, self._writer = await asyncio.open_connection(
                host=self._host, port=self._port, sock=sock
            )
        except Exception as e:
            self.connection_state.emit(camera_id, f"Connect failed: {e}")
            return

        self.connection_state.emit(camera_id, "Connected")

        # Step 1: Send connect XML
        connect_xml = (
            '<?xml version="1.0" encoding="utf-8"?>'
            '<methodcall><requestid>0</requestid>'
            f'<methodname>connect</methodname>'
            f'<username>a</username><password>a</password>'
            f'<cameraid>{camera_id}</cameraid>'
            f'<alwaysstdjpeg>yes</alwaysstdjpeg>'
            f'<transcode><allframes>yes</allframes></transcode>'
            f'<connectparam>id={camera_id}&amp;connectiontoken={token}'
            f'</connectparam></methodcall>\r\n\r\n'
        )
        self._writer.write(connect_xml.encode())
        await self._writer.drain()

        # Step 2: Send live XML
        live_xml = (
            '<?xml version="1.0" encoding="utf-8"?>'
            '<methodcall><requestid>1</requestid>'
            '<methodname>live</methodname>'
            '<compressionrate>90</compressionrate>'
            '</methodcall>\r\n\r\n'
        )
        self._writer.write(live_xml.encode())
        await self._writer.drain()

        # Step 3: Read JPEG frames in a loop
        await self._read_frames()

    async def _read_frames(self):
        """Read JPEG frames from the ImageServer."""
        buffer = b""
        frame_count = 0

        while self._running and self._reader:
            try:
                chunk = await asyncio.wait_for(self._reader.read(65536), timeout=30)
                if not chunk:
                    break

                buffer += chunk

                # Extract JPEG frames: look for JPEG markers
                while True:
                    # Find JPEG start marker (FF D8)
                    start = buffer.find(b'\xff\xd8')
                    if start < 0:
                        # No complete frame yet — keep buffering
                        if len(buffer) > 10 * 1024 * 1024:
                            buffer = buffer[-1024 * 1024:]
                        break

                    # Find JPEG end marker (FF D9)
                    end = buffer.find(b'\xff\xd9', start)
                    if end < 0:
                        # Incomplete frame — keep buffering
                        break

                    # Found a complete JPEG frame
                    jpeg_data = buffer[start:end + 2]
                    buffer = buffer[end + 2:]
                    frame_count += 1

                    # Convert JPEG bytes to QImage and emit
                    qimg = QImage()
                    if qimg.loadFromData(jpeg_data, "JPEG"):
                        self.frame_received.emit(self._camera_id, qimg)

            except asyncio.TimeoutError:
                self.connection_state.emit(self._camera_id, "Timeout")
                break
            except Exception as e:
                self.connection_state.emit(self._camera_id, f"Error: {e}")
                break

        self.connection_state.emit(self._camera_id, "Disconnected")

    async def stop(self):
        self._running = False
        if self._writer:
            self._writer.close()
            try:
                await self._writer.wait_closed()
            except Exception:
                pass
