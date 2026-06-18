"""
MilestoneApplication — Qt application setup + main window
"""
import asyncio
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from src.ui.main_window import MainWindow
from src.core.config import AppConfig


class MilestoneApplication:
    def __init__(self, config: AppConfig):
        self._config = config
        self._qapp = QApplication([])
        self._qapp.setApplicationName("Milestone Smart Client")
        self._qapp.setOrganizationName("Milestone Systems")
        self._loop = asyncio.new_event_loop()
        self._window = MainWindow(config, self._loop)

        # Async loop integration: tick the asyncio loop every 10ms
        self._timer = QTimer()
        self._timer.timeout.connect(self._tick_async)
        self._timer.start(10)

    def _tick_async(self):
        self._loop.stop()
        self._loop.run_forever()

    def run(self):
        self._window.show()
        self._qapp.exec()
