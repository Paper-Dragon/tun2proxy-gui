from __future__ import annotations

import os
import platform
import sys
from pathlib import Path


def platform_key() -> str:
    if sys.platform == "win32":
        return "windows"
    if sys.platform == "darwin":
        return "macos"
    return "linux"


def arch_key() -> str:
    machine = platform.machine().lower()
    if machine in ("amd64", "x86_64", "x64"):
        return "x86_64"
    if machine in ("arm64", "aarch64"):
        return "aarch64"
    if machine in ("i386", "i686", "x86"):
        return "i686"
    if machine.startswith("armv7"):
        return "armv7"
    return machine or "unknown"


def app_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def _meipass() -> Path | None:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return None


def _first_existing(*candidates: Path) -> Path:
    for path in candidates:
        if path.exists():
            return path
    return candidates[0]


def _bin_roots() -> list[Path]:
    roots = [app_root() / "bin"]
    meipass = _meipass()
    if meipass is not None:
        roots.append(meipass / "bin")
    return roots


def resource_root() -> Path:
    meipass = _meipass()
    candidates: list[Path] = []
    if meipass is not None:
        candidates.append(meipass / "resources")
        candidates.append(meipass)
    candidates.append(app_root() / "resources")
    return _first_existing(*candidates)


def bin_dir() -> Path:
    key = platform_key()
    arch = arch_key()
    candidates: list[Path] = []
    for root in _bin_roots():
        candidates.append(root / key / arch)
        candidates.append(root / key)
        candidates.append(root)
    return _first_existing(*candidates)


def tun2proxy_bin_name() -> str:
    return "tun2proxy-bin.exe" if sys.platform == "win32" else "tun2proxy-bin"


def tun2proxy_bin() -> Path:
    name = tun2proxy_bin_name()
    key = platform_key()
    arch = arch_key()
    candidates: list[Path] = []
    for root in _bin_roots():
        candidates.append(root / key / arch / name)
        candidates.append(root / key / name)
        candidates.append(root / name)
    return _first_existing(*candidates)


def tun2proxy_exe() -> Path:
    return tun2proxy_bin()


def icon_path() -> Path:
    root = resource_root()
    if sys.platform == "win32":
        return _first_existing(root / "icon.ico", root / "icon.png")
    return _first_existing(root / "icon.png", root / "icon.ico")


def config_dir() -> Path:
    if sys.platform == "win32":
        base = Path.home() / "AppData" / "Roaming"
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        xdg = os.environ.get("XDG_CONFIG_HOME", "").strip()
        base = Path(xdg) if xdg else Path.home() / ".config"
    path = base / "tun2proxy-gui"
    path.mkdir(parents=True, exist_ok=True)
    return path


def config_file() -> Path:
    return config_dir() / "config.json"
