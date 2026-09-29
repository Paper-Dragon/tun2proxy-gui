# -*- mode: python ; coding: utf-8 -*-

import platform
import sys
from pathlib import Path

block_cipher = None
root = Path(SPECPATH)


def _platform_key() -> str:
    if sys.platform == "win32":
        return "windows"
    if sys.platform == "darwin":
        return "macos"
    return "linux"


def _arch_key() -> str:
    machine = platform.machine().lower()
    if machine in ("amd64", "x86_64", "x64"):
        return "x86_64"
    if machine in ("arm64", "aarch64"):
        return "aarch64"
    if machine in ("i386", "i686", "x86"):
        return "i686"
    return machine or "unknown"


def _bin_datas() -> list[tuple[str, str]]:
    key = _platform_key()
    arch = _arch_key()
    candidates = [
        root / "bin" / key / arch,
        root / "bin" / key,
        root / "bin",
    ]
    for src in candidates:
        if src.exists():
            if src == root / "bin":
                return [(str(src), "bin")]
            rel = src.relative_to(root / "bin").as_posix()
            return [(str(src), f"bin/{rel}")]
    return [(str(root / "bin"), "bin")]


a = Analysis(
    [str(root / "main.py")],
    pathex=[str(root)],
    binaries=[],
    datas=[
        *_bin_datas(),
        (str(root / "resources"), "resources"),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe_kwargs = dict(
    exclude_binaries=True,
    name="Tun2ProxyGUI",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

if sys.platform == "win32":
    exe_kwargs["uac_admin"] = True
    exe_kwargs["icon"] = str(root / "resources" / "icon.ico")
elif (root / "resources" / "icon.png").exists():
    exe_kwargs["icon"] = str(root / "resources" / "icon.png")

exe = EXE(
    pyz,
    a.scripts,
    [],
    **exe_kwargs,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="Tun2ProxyGUI",
)
