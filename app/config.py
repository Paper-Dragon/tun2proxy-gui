"""Persistent configuration for Tun2Proxy GUI."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any

from .paths import config_file


@dataclass
class AppConfig:
    proxy_url: str = ""
    dns_strategy: str = "virtual"  # virtual | over-tcp | direct
    dns_addr: str = "8.8.8.8"
    bypass: list[str] = field(default_factory=list)
    # advanced tun2proxy options
    tun: str = ""
    virtual_dns_pool: str = "198.18.0.0/15"
    verbosity: str = "info"
    ipv6_enabled: bool = False
    tcp_timeout: int = 600
    udp_timeout: int = 10
    max_sessions: int = 200
    udpgw_server: str = ""
    udpgw_connections: int = 5
    udpgw_keepalive: int = 30
    exit_on_fatal_error: bool = False
    # app behavior
    close_to_tray: bool = True
    autostart: bool = False
    start_minimized: bool = False

    def bypass_text(self) -> str:
        return "\n".join(self.bypass)

    def set_bypass_text(self, text: str) -> None:
        lines = []
        for line in text.replace(",", "\n").splitlines():
            item = line.strip()
            if item and not item.startswith("#"):
                lines.append(item)
        self.bypass = lines

    def to_cli_args(self) -> list[str]:
        args = [
            "--proxy",
            self.proxy_url.strip(),
            "--dns",
            self.dns_strategy,
            "--dns-addr",
            self.dns_addr.strip() or "8.8.8.8",
            "--verbosity",
            self.verbosity,
            "--tcp-timeout",
            str(self.tcp_timeout),
            "--udp-timeout",
            str(self.udp_timeout),
            "--max-sessions",
            str(self.max_sessions),
        ]
        if self.tun.strip():
            args.extend(["--tun", self.tun.strip()])
        pool = self.virtual_dns_pool.strip()
        if pool and pool != "198.18.0.0/15":
            args.extend(["--virtual-dns-pool", pool])
        if self.ipv6_enabled:
            args.append("--ipv6-enabled")
        for cidr in self.bypass:
            args.extend(["--bypass", cidr])
        if self.udpgw_server.strip():
            args.extend(["--udpgw-server", self.udpgw_server.strip()])
            if self.udpgw_connections != 5:
                args.extend(["--udpgw-connections", str(self.udpgw_connections)])
            if self.udpgw_keepalive != 30:
                args.extend(["--udpgw-keepalive", str(self.udpgw_keepalive)])
        if self.exit_on_fatal_error:
            args.append("--exit-on-fatal-error")
        return args

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AppConfig:
        from dataclasses import fields

        known = {f.name for f in fields(cls)}
        filtered = {k: v for k, v in data.items() if k in known}
        if "bypass" in filtered and isinstance(filtered["bypass"], str):
            filtered["bypass"] = [
                line.strip()
                for line in filtered["bypass"].replace(",", "\n").splitlines()
                if line.strip()
            ]
        return cls(**filtered)


def load_config() -> AppConfig:
    path = config_file()
    if not path.exists():
        return AppConfig()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return AppConfig()
        return AppConfig.from_dict(data)
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        return AppConfig()


def save_config(config: AppConfig) -> None:
    path = config_file()
    path.write_text(
        json.dumps(asdict(config), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
