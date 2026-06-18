"""
Milestone Linux Smart Client — Entry Point

Launches the PySide6 application with qasync for proper asyncio integration.
"""
import asyncio
import sys

import qasync
from PySide6.QtWidgets import QApplication

from src.core.config import load_config
from src.ui.main_window import MainWindow


def main():
    config = load_config()
    app = QApplication(sys.argv)
    app.setApplicationName("Milestone Smart Client")
    app.setOrganizationName("Milestone Systems")

    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)

    window = MainWindow(config)
    window.show()

    with loop:
        loop.run_forever()


if __name__ == "__main__":
    main()
