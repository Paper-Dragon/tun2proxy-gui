from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication, QMessageBox, QSystemTrayIcon

from app.elevate import is_admin, relaunch_as_admin
from app.main_window import MainWindow


def _elevation_prompt_text() -> tuple[str, str]:
    if sys.platform == "win32":
        return (
            "需要管理员权限",
            "Tun2Proxy 需要管理员权限才能创建 TUN 设备并配置路由。\n\n是否以管理员身份重新启动？",
        )
    if sys.platform == "darwin":
        return (
            "需要管理员权限",
            "Tun2Proxy 需要管理员权限才能创建 TUN 设备并配置路由。\n\n是否输入密码以提升权限后重新启动？",
        )
    return (
        "需要管理员权限",
        "Tun2Proxy 需要 root 权限才能创建 TUN 设备并配置路由。\n\n是否以提升权限重新启动？",
    )


def main() -> int:
    args = sys.argv[1:]
    start_minimized = "--minimized" in args
    skip_elevate = "--no-elevate" in args

    app = QApplication(sys.argv)
    app.setApplicationName("Tun2Proxy GUI")
    app.setOrganizationName("tun2proxy-gui")
    app.setQuitOnLastWindowClosed(False)

    if not skip_elevate and not is_admin():
        title, body = _elevation_prompt_text()
        reply = QMessageBox.question(
            None,
            title,
            body,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )
        if reply == QMessageBox.StandardButton.Yes:
            if relaunch_as_admin(extra_args=["--minimized"] if start_minimized else None):
                return 0
            hint = (
                "请手动右键「以管理员身份运行」。"
                if sys.platform == "win32"
                else "请使用 sudo / pkexec 手动启动，或检查系统是否允许图形化提权。"
            )
            QMessageBox.critical(None, "提权失败", f"无法以提升权限启动。{hint}")
            return 1

    if not QSystemTrayIcon.isSystemTrayAvailable():
        QMessageBox.warning(None, "提示", "系统托盘不可用，关闭窗口将直接退出。")

    window = MainWindow(start_minimized=start_minimized)
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
