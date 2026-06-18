"""
MainWindow — central application window with multi-view video grid

Phase 1: Single live camera view via WebRTC
"""
import asyncio
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QGridLayout, QPushButton,
    QStatusBar, QMenuBar, QToolBar, QMessageBox,
    QDockWidget, QTreeWidget, QTreeWidgetItem, QTabWidget,
    QSizePolicy,
)
from PySide6.QtCore import Qt
from src.core.config import AppConfig
from src.core.event_bus import event_bus
from src.core.session import ServerSession, SessionManager
from src.ui.camera_view_widget import CameraViewWidget
from src.ui.ptz_control_panel import PTZControlPanel
from src.ui.alarm_panel import AlarmPanel
from src.ui.playback_timeline import PlaybackTimeline
from src.ui.settings_dialog import SettingsDialog


class MainWindow(QMainWindow):
    def __init__(self, config: AppConfig):
        super().__init__()
        self._config = config
        self._grid_rows = 1
        self._grid_cols = 1
        self._camera_views: dict[str, CameraViewWidget] = {}
        self._session: ServerSession | None = None
        self._init_ui()
        event_bus.status_message.connect(self._status.showMessage)
        event_bus.connected.connect(lambda s: self._status.showMessage(f"Connected to {s}"))
        event_bus.disconnected.connect(lambda: self._status.showMessage("Disconnected"))

    def _init_ui(self):
        self.setWindowTitle("Milestone Smart Client")
        self.resize(1400, 900)

        # Menu
        mb = self.menuBar()
        fm = mb.addMenu("&File")
        fm.addAction("&Connect...", self._on_connect).setShortcut("Ctrl+C")
        fm.addAction("&Disconnect", self._on_disconnect).setShortcut("Ctrl+D")
        fm.addSeparator()
        fm.addAction("E&xit", self.close).setShortcut("Ctrl+Q")
        vm = mb.addMenu("&View")
        for label, r, c in [("1×1", 1, 1), ("2×2", 2, 2), ("3×3", 3, 3), ("4×4", 4, 4)]:
            vm.addAction(label, lambda r=r, c=c: self._rebuild_grid(r, c))
        tm = mb.addMenu("&Tools")
        tm.addAction("&ONVIF Discovery...", self._on_discovery)

        # Toolbar
        tb = QToolBar("Main")
        self.addToolBar(tb)
        tb.addAction("Connect", self._on_connect)
        for label, r, c in [("1×1",1,1), ("2×2",2,2), ("4×4",4,4)]:
            tb.addAction(label, lambda r=r, c=c: self._rebuild_grid(r, c))

        # Central grid
        self._grid_widget = QWidget()
        self._grid_layout = QGridLayout(self._grid_widget)
        self._grid_layout.setSpacing(2)
        self.setCentralWidget(self._grid_widget)
        self._rebuild_grid(1, 1)

        # Left dock: camera tree
        self._camera_tree = QTreeWidget()
        self._camera_tree.setHeaderLabel("Cameras")
        self._camera_tree.itemDoubleClicked.connect(self._on_camera_clicked)
        d = QDockWidget("Cameras", self)
        d.setWidget(self._camera_tree)
        self.addDockWidget(Qt.LeftDockWidgetArea, d)

        # Right dock: alarms + PTZ
        tabs = QTabWidget()
        tabs.addTab(AlarmPanel(), "Alarms")
        tabs.addTab(PTZControlPanel(), "PTZ")
        d = QDockWidget("Controls", self)
        d.setWidget(tabs)
        self.addDockWidget(Qt.RightDockWidgetArea, d)

        # Bottom dock: timeline
        d = QDockWidget("Timeline", self)
        d.setWidget(PlaybackTimeline())
        self.addDockWidget(Qt.BottomDockWidgetArea, d)

        # Status bar
        self._status = QStatusBar()
        self.setStatusBar(self._status)
        self._status.showMessage("Ready — File > Connect")

    def _rebuild_grid(self, rows: int, cols: int):
        self._grid_rows, self._grid_cols = rows, cols
        while self._grid_layout.count():
            item = self._grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._camera_views.clear()
        for r in range(rows):
            for c in range(cols):
                v = CameraViewWidget()
                v.setMinimumSize(320, 240)
                v.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                self._grid_layout.addWidget(v, r, c)
                self._camera_views[f"{r}_{c}"] = v

    # ── Connection ──────────────────────────────────────────────────

    def _on_connect(self):
        dlg = SettingsDialog(self._config, self)
        if dlg.exec():
            asyncio.ensure_future(self._do_connect(dlg.get_config()))

    async def _do_connect(self, cfg: dict):
        self._status.showMessage(f"Connecting to {cfg['server_url']}...")
        try:
            session = ServerSession(
                server_url=cfg["server_url"],
                api_gateway_url=cfg["api_gateway_url"],
                username=cfg["username"],
                bridge_host=cfg.get("bridge_host", ""),
                bridge_port=cfg.get("bridge_port", 50051),
            )
            await session.connect(cfg["password"])
            self._session = session
            SessionManager().add("default", session)

            # Camera tree via REST
            from src.services.camera_service import CameraService
            svc = CameraService(session.config_api, session.bridge)
            root = await svc.refresh()
            self._camera_tree.clear()
            for cam in root.cameras:
                item = QTreeWidgetItem([cam.name])
                item.setData(0, Qt.UserRole, cam.id)
                item.setToolTip(0, f"{cam.name} [{cam.id}]")
                self._camera_tree.addTopLevelItem(item)

            event_bus.connected.emit(cfg["server_url"])
        except Exception as e:
            QMessageBox.critical(self, "Connection Failed", str(e))
            self._status.showMessage("Connection failed")

    def _on_disconnect(self):
        if self._session:
            asyncio.ensure_future(self._session.disconnect())
            self._session = None
        event_bus.disconnected.emit()

    # ── Camera to grid ──────────────────────────────────────────────

    def _on_camera_clicked(self, item: QTreeWidgetItem, _col: int):
        cam_id = item.data(0, Qt.UserRole)
        if not cam_id or not self._session:
            return
        for name, view in self._camera_views.items():
            if not view.camera_id:
                asyncio.ensure_future(view.start_stream(self._session, cam_id))
                break

    def _on_discovery(self):
        self._status.showMessage("ONVIF discovery — not yet wired to UI")
