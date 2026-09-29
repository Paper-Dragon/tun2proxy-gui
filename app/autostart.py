"""Windows startup (HKCU Run) helpers."""

from __future__ import annotations

import sys
from pathlib import Path

RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
VALUE_NAME = "Tun2ProxyGUI"


def _winreg():
    import winreg

    return winreg


def launch_command(minimized: bool = True) -> str:
    if getattr(sys, "frozen", False):
        exe = Path(sys.executable).resolve()
        cmd = f'"{exe}"'
    else:
        python = Path(sys.executable).resolve()
        script = Path(sys.argv[0]).resolve()
        cmd = f'"{python}" "{script}"'
    if minimized:
        cmd += " --minimized"
    return cmd


def is_enabled() -> bool:
    if sys.platform != "win32":
        return False
    winreg = _winreg()
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_READ) as key:
            winreg.QueryValueEx(key, VALUE_NAME)
            return True
    except OSError:
        return False


def set_enabled(enabled: bool, minimized: bool = True) -> None:
    if sys.platform != "win32":
        return
    winreg = _winreg()
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
        if enabled:
            winreg.SetValueEx(key, VALUE_NAME, 0, winreg.REG_SZ, launch_command(minimized))
        else:
            try:
                winreg.DeleteValue(key, VALUE_NAME)
            except FileNotFoundError:
                pass
