"""
Milestone Linux Smart Client — Entry Point
"""
import sys
import asyncio
from PySide6.QtWidgets import QApplication
from src.core.config import load_config
from src.ui.app import MilestoneApplication


def main():
    config = load_config()
    app = MilestoneApplication(config)
    app.run()


if __name__ == "__main__":
    main()
