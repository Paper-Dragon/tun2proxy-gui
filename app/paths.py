"""Resolve resource paths for development and PyInstaller builds."""

from __future__ import annotations

import sys
from pathlib import Path


def app_root() -> Path:
    """Directory that contains the application executable (and often adjacent ``bin``)."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def _meipass() -> Path | None:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)  # type: ignore[attr-defined]
    return None


def _first_existing(*candidates: Path) -> Path:
    for path in candidates:
        if path.exists():
            return path
    return candidates[0]


def resource_root() -> Path:
    """Directory for bundled resources (icons, etc.)."""
    meipass = _meipass()
    candidates: list[Path] = []
    if meipass is not None:
        candidates.append(meipass / "resources")
        candidates.append(meipass)
    candidates.append(app_root() / "resources")
    return _first_existing(*candidates)


def bin_dir() -> Path:
    meipass = _meipass()
    candidates: list[Path] = [app_root() / "bin"]
    if meipass is not None:
        candidates.append(meipass / "bin")
    return _first_existing(*candidates)


def tun2proxy_exe() -> Path:
    return bin_dir() / "tun2proxy-bin.exe"


def icon_path() -> Path:
    return resource_root() / "icon.ico"


def config_dir() -> Path:
    appdata = Path.home() / "AppData" / "Roaming" / "tun2proxy-gui"
    appdata.mkdir(parents=True, exist_ok=True)
    return appdata


def config_file() -> Path:
    return config_dir() / "config.json"
