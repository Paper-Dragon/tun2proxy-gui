"""Windows UAC elevation helpers."""

from __future__ import annotations

import ctypes
import sys
from pathlib import Path


def is_admin() -> bool:
    if sys.platform != "win32":
        return True
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def relaunch_as_admin(extra_args: list[str] | None = None) -> bool:
    """Relaunch the current process elevated. Returns True if elevation was requested."""
    if sys.platform != "win32":
        return False

    params = list(sys.argv[1:])
    if extra_args:
        for arg in extra_args:
            if arg not in params:
                params.append(arg)

    if getattr(sys, "frozen", False):
        executable = sys.executable
        # Quote each argument for ShellExecute
        param_str = " ".join(f'"{p}"' if " " in p else p for p in params)
    else:
        executable = sys.executable
        script = str(Path(sys.argv[0]).resolve())
        quoted_script = f'"{script}"' if " " in script else script
        rest = " ".join(f'"{p}"' if " " in p else p for p in params)
        param_str = f"{quoted_script} {rest}".strip()

    # SW_SHOWNORMAL = 1
    ret = ctypes.windll.shell32.ShellExecuteW(
        None,
        "runas",
        executable,
        param_str,
        None,
        1,
    )
    # > 32 means success
    return int(ret) > 32
