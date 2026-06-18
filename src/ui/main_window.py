"""
MainWindow — the central application window with multi-view grid layout
"""
import asyncio
from PySide6.QtWidgets import (
    QMainWindow, QSplitter, QTreeWidget, QTreeWidgetItem,
    QWidget, QGridLayout, QVBoxLayout, QHBoxLayout,
    QPushButton, QStatusBar, QMenuBar, QMenu,
    QDockWidget, QListWidget, QTabWidget, QToolBar,
)
from PySide6.QtCore import Qt
from src.core.config import AppConfig
from src.core.event_bus import event_bus
from src.ui.camera_view_widget import CameraViewWidget
from src.ui.ptz_control_panel import PTZControlPanel
from src.ui.alarm_panel import AlarmPanel
from src.ui.playback_timeline import PlaybackTimeline


class MainWindow(QMainWindow):
    """Main application window with multi-view video grid."""

    def __init__(self, config: AppConfig, loop: asyncio.AbstractEventLoop):
        super().__init__()
        self._config = config
        self._loop = loop
        self._grid_rows = 1
        self._grid_cols = 1
        self._camera_views: dict[str, CameraViewWidget] = {}
        self._session = None  # ServerSession, set on connect

        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle("Milestone Smart Client — Linux")
        self.resize(1400, 900)

        # Central video grid
        self._grid_widget = QWidget()
        self._grid_layout = QGridLayout(self._grid_widget)
        self._grid_layout.setSpacing(2)
        self.setCentralWidget(self._grid_widget)
        self._rebuild_grid(1, 1)

        # Left dock — camera tree
        self._camera_tree = QTreeWidget()
        self._camera_tree.setHeaderLabel("Cameras")
        self._camera_tree.itemDoubleClicked.connect(self._on_camera_selected)
        tree_dock = QDockWidget("Cameras", self)
        tree_dock.setWidget(self._camera_tree)
        self.addDockWidget(Qt.LeftDockWidgetArea, tree_dock)

        # Right dock — tabs for alarms + PTZ
        right_tabs = QTabWidget()
        self._alarm_panel = AlarmPanel()
        right_tabs.addTab(self._alarm_panel, "Alarms")
        self._ptz_panel = PTZControlPanel()
        right_tabs.addTab(self._ptz_panel, "PTZ")
        right_dock = QDockWidget("Controls", self)
        right_dock.setWidget(right_tabs)
        self.addDockWidget(Qt.RightDockWidgetArea, right_dock)

        # Bottom dock — playback timeline
        self._timeline = PlaybackTimeline()
        bottom_dock = QDockWidget("Timeline", self)
        bottom_dock.setWidget(self._timeline)
        self.addDockWidget(Qt.BottomDockWidgetArea, bottom_dock)

        # Status bar
        self._status = QStatusBar()
        self.setStatusBar(self._status)
        self._status.showMessage("Disconnected — File > Connect to set up server")

        # Menu bar
        menubar = self.menuBar()
        file_menu = menubar.addMenu("&File")
        file_menu.addAction("&Connect...", self._on_connect)
        file_menu.addAction("&Disconnect", self._on_disconnect)
        file_menu.addSeparator()
        file_menu.addAction("E&xit", self.close)

        view_menu = menubar.addMenu("&View")
        view_menu.addAction("1×1", lambda: self._rebuild_grid(1, 1))
        view_menu.addAction("2×2", lambda: self._rebuild_grid(2, 2))
        view_menu.addAction("3×3", lambda: self._rebuild_grid(3, 3))
        view_menu.addAction("4×4", lambda: self._rebuild_grid(4, 4))

        tools_menu = menubar.addMenu("&Tools")
        tools_menu.addAction("&ONVIF Discovery...", self._on_discovery)

        # Toolbar
        toolbar = QToolBar("Main")
        self.addToolBar(toolbar)
        grid_btn = toolbar.addAction("2×2")
        grid_btn.triggered.connect(lambda: self._rebuild_grid(2, 2))

        # Connect event bus signals
        event_bus.status_message.connect(self._status.showMessage)

    def _rebuild_grid(self, rows: int, cols: int):
        """Rebuild the central video grid."""
        self._grid_rows = rows
        self._grid_cols = cols

        # Clear existing
        while self._grid_layout.count():
            item = self._grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for r in range(rows):
            for c in range(cols):
                view = CameraViewWidget()
                self._grid_layout.addWidget(view, r, c)
                # Store by position index
                idx = r * cols + c
                self._camera_views[f"slot_{idx}"] = view

    def _on_camera_selected(self, item: QTreeWidgetItem, _column: int):
        """Drag camera into first empty grid slot."""
        camera_id = item.data(0, Qt.UserRole)
        if not camera_id:
            return

        # Find first empty slot
        for slot_name, view in self._camera_views.items():
            if not view.camera_id:
                future = asyncio.run_coroutine_threadsafe(
                    self._start_camera_in_view(view, camera_id), self._loop
                )
                break

    async def _start_camera_in_view(self, view: CameraViewWidget, camera_id: str):
        event_bus.status_message.emit(f"Starting camera {camera_id}...")
        # Get session from session manager
        from src.core.session import SessionManager
        sm = SessionManager()
        session = sm.get()
        if not session or not session.connected:
            event_bus.status_message.emit("Not connected to server")
            return

        device_id = camera_id
        await view.start_stream(session, device_id)

    def _on_connect(self):
        """Show connection dialog."""
        from src.ui.settings_dialog import SettingsDialog
        dialog = SettingsDialog(self._config, self)
        if dialog.exec():
            future = asyncio.run_coroutine_threadsafe(
                self._do_connect(dialog.get_config()), self._loop
            )

    async def _do_connect(self, config):
        from src.core.session import ServerSession, SessionManager
        session = ServerSession(
            server_url=config["server_url"],
            api_gateway_url=config["api_gateway_url"],
            username=config["username"],
        )
        await session.connect(config["password"])
        sm = SessionManager()
        sm.add("default", session)

        # Populate camera tree
        from src.services.camera_service import CameraService
        svc = CameraService(session.mobile)
        root = await svc.refresh()
        self._camera_tree.clear()
        for cam in root.cameras:
            item = QTreeWidgetItem([cam.name])
            item.setData(0, Qt.UserRole, cam.id)
            self._camera_tree.addTopLevelItem(item)

        event_bus.connected.emit(config.get("name", "default"))
        event_bus.status_message.emit(f"Connected to {config['server_url']}")

    def _on_disconnect(self):
        event_bus.status_message.emit("Disconnected")

    def _on_discovery(self):
        """Open ONVIF discovery dialog."""
        event_bus.status_message.emit("Scanning for ONVIF devices...")
