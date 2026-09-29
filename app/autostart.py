from __future__ import annotations

import os
import sys
from pathlib import Path

APP_NAME = "Tun2ProxyGUI"
LINUX_DESKTOP_NAME = "tun2proxy-gui.desktop"
MACOS_LABEL = "com.tun2proxy.gui"
MACOS_PLIST_NAME = f"{MACOS_LABEL}.plist"
WIN_RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
WIN_VALUE_NAME = APP_NAME


def launch_argv(minimized: bool = True) -> list[str]:
    if getattr(sys, "frozen", False):
        argv = [str(Path(sys.executable).resolve())]
    else:
        argv = [
            str(Path(sys.executable).resolve()),
            str(Path(sys.argv[0]).resolve()),
        ]
    if minimized:
        argv.append("--minimized")
    return argv


def launch_command(minimized: bool = True) -> str:
    parts = []
    for item in launch_argv(minimized):
        if " " in item:
            parts.append(f'"{item}"')
        else:
            parts.append(item)
    return " ".join(parts)


def is_enabled() -> bool:
    if sys.platform == "win32":
        return _win_is_enabled()
    if sys.platform == "darwin":
        return _macos_plist_path().exists()
    return _linux_desktop_path().exists()


def set_enabled(enabled: bool, minimized: bool = True) -> None:
    if sys.platform == "win32":
        _win_set_enabled(enabled, minimized)
    elif sys.platform == "darwin":
        _macos_set_enabled(enabled, minimized)
    else:
        _linux_set_enabled(enabled, minimized)


def _winreg():
    import winreg

    return winreg


def _win_is_enabled() -> bool:
    winreg = _winreg()
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, WIN_RUN_KEY, 0, winreg.KEY_READ) as key:
            winreg.QueryValueEx(key, WIN_VALUE_NAME)
            return True
    except OSError:
        return False


def _win_set_enabled(enabled: bool, minimized: bool) -> None:
    winreg = _winreg()
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, WIN_RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
        if enabled:
            winreg.SetValueEx(key, WIN_VALUE_NAME, 0, winreg.REG_SZ, launch_command(minimized))
        else:
            try:
                winreg.DeleteValue(key, WIN_VALUE_NAME)
            except FileNotFoundError:
                pass


def _linux_desktop_path() -> Path:
    xdg = os.environ.get("XDG_CONFIG_HOME", "").strip()
    base = Path(xdg) if xdg else Path.home() / ".config"
    return base / "autostart" / LINUX_DESKTOP_NAME


def _linux_set_enabled(enabled: bool, minimized: bool) -> None:
    path = _linux_desktop_path()
    if not enabled:
        if path.exists():
            path.unlink()
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    exec_line = launch_command(minimized)
    content = "\n".join(
        [
            "[Desktop Entry]",
            "Type=Application",
            f"Name={APP_NAME}",
            f"Exec={exec_line}",
            "X-GNOME-Autostart-enabled=true",
            "Hidden=false",
            "NoDisplay=false",
            "",
        ]
    )
    path.write_text(content, encoding="utf-8")


def _macos_plist_path() -> Path:
    return Path.home() / "Library" / "LaunchAgents" / MACOS_PLIST_NAME


def _macos_escape(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _macos_set_enabled(enabled: bool, minimized: bool) -> None:
    path = _macos_plist_path()
    if not enabled:
        if path.exists():
            path.unlink()
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    args_xml = "\n".join(
        f"        <string>{_macos_escape(arg)}</string>" for arg in launch_argv(minimized)
    )
    content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{MACOS_LABEL}</string>
    <key>ProgramArguments</key>
    <array>
{args_xml}
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
"""
    path.write_text(content, encoding="utf-8")
