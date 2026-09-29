"""Tun2Proxy GUI entry point."""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication, QMessageBox, QSystemTrayIcon

from app.elevate import is_admin, relaunch_as_admin
from app.main_window import MainWindow


def main() -> int:
    args = sys.argv[1:]
    start_minimized = "--minimized" in args
    skip_elevate = "--no-elevate" in args

    app = QApplication(sys.argv)
    app.setApplicationName("Tun2Proxy GUI")
    app.setOrganizationName("tun2proxy-gui")
    app.setQuitOnLastWindowClosed(False)

    if sys.platform == "win32" and not skip_elevate and not is_admin():
        reply = QMessageBox.question(
            None,
            "需要管理员权限",
            "Tun2Proxy 需要管理员权限才能创建 TUN 设备并配置路由。\n\n是否以管理员身份重新启动？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )
        if reply == QMessageBox.StandardButton.Yes:
            if relaunch_as_admin(extra_args=["--minimized"] if start_minimized else None):
                return 0
            QMessageBox.critical(None, "提权失败", "无法以管理员身份启动，请手动右键「以管理员身份运行」。")
            return 1
        # User declined — continue anyway (may fail at runtime)

    if not QSystemTrayIcon.isSystemTrayAvailable():
        QMessageBox.warning(None, "提示", "系统托盘不可用，关闭窗口将直接退出。")

    window = MainWindow(start_minimized=start_minimized)
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
