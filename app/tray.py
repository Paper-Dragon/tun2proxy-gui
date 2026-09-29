"""System tray icon and menu."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QMenu, QSystemTrayIcon, QWidget

from .paths import icon_path
from .process_manager import ProxyState


class TrayController:
    def __init__(
        self,
        window: QWidget,
        *,
        on_toggle: Callable[[], None],
        on_show: Callable[[], None],
        on_quit: Callable[[], None],
    ) -> None:
        self._window = window
        self._on_show = on_show
        self._icon = QIcon(str(icon_path())) if icon_path().exists() else QIcon()

        self.tray = QSystemTrayIcon(self._icon, window)
        self.tray.setToolTip("Tun2Proxy GUI")

        menu = QMenu(window)
        self.action_show = QAction("显示主窗口", window)
        self.action_toggle = QAction("连接", window)
        self.action_quit = QAction("退出", window)

        self.action_show.triggered.connect(on_show)
        self.action_toggle.triggered.connect(on_toggle)
        self.action_quit.triggered.connect(on_quit)

        menu.addAction(self.action_show)
        menu.addAction(self.action_toggle)
        menu.addSeparator()
        menu.addAction(self.action_quit)

        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self._on_activated)
        self.tray.show()

    def _on_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._on_show()

    def update_state(self, state: ProxyState, running: bool) -> None:
        if running:
            self.action_toggle.setText("断开")
            tip = "Tun2Proxy — 已连接"
        else:
            self.action_toggle.setText("连接")
            if state == ProxyState.ERROR:
                tip = "Tun2Proxy — 连接失败"
            else:
                tip = "Tun2Proxy — 未连接"
        self.tray.setToolTip(tip)

    def show_message(self, title: str, message: str) -> None:
        self.tray.showMessage(title, message, QSystemTrayIcon.MessageIcon.Information, 3000)

    def hide(self) -> None:
        self.tray.hide()
