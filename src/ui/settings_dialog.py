"""
Settings Dialog — server connection configuration
"""
from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QComboBox,
    QDialogButtonBox, QVBoxLayout, QGroupBox,
)


class SettingsDialog(QDialog):
    """Connection settings dialog."""

    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Connect to XProtect Server")
        self._config = config
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        group = QGroupBox("Server Connection")
        form = QFormLayout(group)

        self._server_url = QLineEdit()
        self._server_url.setPlaceholderText("milestone.putnamcountytn.gov")
        form.addRow("Server URL:", self._server_url)

        self._username = QLineEdit()
        form.addRow("Username:", self._username)

        self._password = QLineEdit()
        self._password.setEchoMode(QLineEdit.Password)
        form.addRow("Password:", self._password)

        self._auth_type = QComboBox()
        self._auth_type.addItems(["basic", "windows"])
        form.addRow("Auth Type:", self._auth_type)

        layout.addWidget(group)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        # Pre-fill from config
        if self._config.servers:
            s = self._config.current_server
            self._server_url.setText(s.server_url)
            self._username.setText(s.username)
            self._auth_type.setCurrentText(s.auth_type)

    def get_config(self) -> dict:
        def normalize(url: str) -> str:
            url = url.strip()
            if url and not url.startswith(("http://", "https://")):
                url = "https://" + url
            url = url.rstrip("/")
            return url

        server_url = normalize(self._server_url.text())
        return {
            "name": "default",
            "server_url": server_url,
            "api_gateway_url": server_url,
            "username": self._username.text(),
            "password": self._password.text(),
            "auth_type": self._auth_type.currentText(),
        }
