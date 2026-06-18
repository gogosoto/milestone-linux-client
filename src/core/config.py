"""
Configuration loader — YAML-based server profiles
"""
import os
from pathlib import Path
import yaml

CONFIG_DIR = Path.home() / ".config" / "milestone-client"
CONFIG_FILE = CONFIG_DIR / "config.yaml"


class ServerConfig:
    def __init__(self, data: dict):
        self.name: str = data.get("name", "default")
        self.server_url: str = data.get("server_url", "")
        self.api_gateway_url: str = data.get("api_gateway_url", "")
        self.username: str = data.get("username", "")
        self.auth_type: str = data.get("auth_type", "basic")  # basic | windows
        self.bridge_host: str = data.get("bridge_host", "")
        self.bridge_port: int = data.get("bridge_port", 50051)


class AppConfig:
    def __init__(self, data: dict):
        self.servers: list[ServerConfig] = [
            ServerConfig(s) for s in data.get("servers", [{"name": "default"}])
        ]
        self.active_server: str = data.get("active_server", "default")
        self.grid_layout: str = data.get("grid_layout", "1x1")
        self.theme: str = data.get("theme", "dark")
        self.recent_servers: list = data.get("recent_servers", [])

    @property
    def current_server(self) -> ServerConfig:
        for s in self.servers:
            if s.name == self.active_server:
                return s
        return self.servers[0]


def load_config() -> AppConfig:
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            return AppConfig(yaml.safe_load(f) or {})
    return AppConfig({})


def save_config(config: AppConfig):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        yaml.dump({
            "servers": [
                {
                    "name": s.name,
                    "server_url": s.server_url,
                    "api_gateway_url": s.api_gateway_url,
                    "username": s.username,
                    "auth_type": s.auth_type,
                    "bridge_host": s.bridge_host,
                    "bridge_port": s.bridge_port,
                }
                for s in config.servers
            ],
            "active_server": config.active_server,
            "grid_layout": config.grid_layout,
            "theme": config.theme,
        }, f)
