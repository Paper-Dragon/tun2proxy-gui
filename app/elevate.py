from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


def is_admin() -> bool:
    if sys.platform == "win32":
        try:
            import ctypes

            return bool(ctypes.windll.shell32.IsUserAnAdmin())
        except Exception:
            return False
    try:
        return os.geteuid() == 0
    except AttributeError:
        return False


def _launch_argv() -> tuple[str, list[str]]:
    if getattr(sys, "frozen", False):
        return sys.executable, list(sys.argv[1:])
    script = str(Path(sys.argv[0]).resolve())
    return sys.executable, [script, *sys.argv[1:]]


def _merge_extra(params: list[str], extra_args: list[str] | None) -> list[str]:
    if not extra_args:
        return params
    merged = list(params)
    for arg in extra_args:
        if arg not in merged:
            merged.append(arg)
    return merged


def relaunch_as_admin(extra_args: list[str] | None = None) -> bool:
    executable, params = _launch_argv()
    params = _merge_extra(params, extra_args)

    if sys.platform == "win32":
        return _relaunch_windows(executable, params)
    if sys.platform == "darwin":
        return _relaunch_macos(executable, params)
    return _relaunch_linux(executable, params)


def _relaunch_windows(executable: str, params: list[str]) -> bool:
    import ctypes

    param_str = " ".join(f'"{p}"' if " " in p else p for p in params)
    ret = ctypes.windll.shell32.ShellExecuteW(
        None,
        "runas",
        executable,
        param_str,
        None,
        1,
    )
    return int(ret) > 32


def _quote_shell(value: str) -> str:
    return "'" + value.replace("'", "'\"'\"'") + "'"


def _relaunch_macos(executable: str, params: list[str]) -> bool:
    cmd = " ".join(_quote_shell(p) for p in [executable, *params])
    escaped = cmd.replace("\\", "\\\\").replace('"', '\\"')
    script = f'do shell script "{escaped}" with administrator privileges'
    try:
        subprocess.Popen(
            ["osascript", "-e", script],
            start_new_session=True,
        )
        return True
    except OSError:
        return False


def _relaunch_linux(executable: str, params: list[str]) -> bool:
    argv = [executable, *params]
    env = os.environ.copy()
    pkexec = shutil.which("pkexec")
    if pkexec:
        try:
            subprocess.Popen(
                [pkexec, "env", f"DISPLAY={env.get('DISPLAY', '')}", f"XAUTHORITY={env.get('XAUTHORITY', '')}", *argv],
                start_new_session=True,
            )
            return True
        except OSError:
            pass

    sudo = shutil.which("sudo")
    if sudo:
        try:
            subprocess.Popen([sudo, "-A", *argv], start_new_session=True, env=env)
            return True
        except OSError:
            try:
                subprocess.Popen([sudo, *argv], start_new_session=True, env=env)
                return True
            except OSError:
                return False
    return False
