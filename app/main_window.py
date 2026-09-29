"""Main application window."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QCloseEvent, QFont, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from . import __version__
from . import autostart
from .config import AppConfig, load_config, save_config
from .paths import icon_path
from .process_manager import ProcessManager, ProxyState
from .styles import APP_STYLESHEET
from .tray import TrayController


class MainWindow(QWidget):
    def __init__(self, start_minimized: bool = False) -> None:
        super().__init__()
        self.setObjectName("MainWindow")
        self.setWindowTitle("Tun2Proxy")
        self.resize(860, 720)
        self.setMinimumSize(720, 600)
        self.setStyleSheet(APP_STYLESHEET)

        icon = icon_path()
        if icon.exists():
            self.setWindowIcon(QIcon(str(icon)))

        self._config = load_config()
        self._force_quit = False
        self._manager = ProcessManager(self)
        self._manager.state_changed.connect(self._on_state_changed)
        self._manager.log_line.connect(self._append_log)
        self._manager.exited.connect(self._on_exited)

        self._build_ui()
        self._load_config_to_ui()

        self._tray = TrayController(
            self,
            on_toggle=self.toggle_proxy,
            on_show=self._show_from_tray,
            on_quit=self.quit_app,
        )
        self._on_state_changed(self._manager.state)

        self.chk_autostart.blockSignals(True)
        self.chk_autostart.setChecked(autostart.is_enabled())
        self.chk_autostart.blockSignals(False)

        if start_minimized or self._config.start_minimized:
            self.hide()
        else:
            self.show()

    # ── layout ──────────────────────────────────────────────

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_topbar())

        body = QVBoxLayout()
        body.setContentsMargins(24, 20, 24, 24)
        body.setSpacing(14)

        body.addWidget(self._build_hero())
        body.addWidget(self._build_drawer())
        body.addWidget(self._build_console(), stretch=1)

        wrap = QWidget()
        wrap.setLayout(body)
        root.addWidget(wrap, stretch=1)

    def _build_topbar(self) -> QFrame:
        bar = QFrame()
        bar.setObjectName("TopBar")
        bar.setFixedHeight(56)
        row = QHBoxLayout(bar)
        row.setContentsMargins(20, 0, 16, 0)
        row.setSpacing(10)

        mark = QLabel()
        mark.setObjectName("LogoMark")
        mark.setFixedSize(32, 32)
        mark.setScaledContents(True)
        icon = icon_path()
        if icon.exists():
            mark.setPixmap(QIcon(str(icon)).pixmap(32, 32))
        else:
            mark.setText("T2")
            mark.setAlignment(Qt.AlignmentFlag.AlignCenter)
        row.addWidget(mark)

        names = QVBoxLayout()
        names.setSpacing(0)
        names.setContentsMargins(0, 8, 0, 8)
        name = QLabel("Tun2Proxy")
        name.setObjectName("AppName")
        meta = QLabel(f"v{__version__}")
        meta.setObjectName("AppMeta")
        names.addWidget(name)
        names.addWidget(meta)
        row.addLayout(names)
        row.addStretch()

        self.btn_settings = QPushButton("设置")
        self.btn_settings.setObjectName("IconBtn")
        self.btn_settings.setCheckable(True)
        self.btn_settings.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_settings.toggled.connect(self._toggle_drawer)
        row.addWidget(self.btn_settings)
        return bar

    def _build_hero(self) -> QFrame:
        hero = QFrame()
        hero.setObjectName("Hero")
        layout = QVBoxLayout(hero)
        layout.setContentsMargins(28, 26, 28, 26)
        layout.setSpacing(14)

        self.status_label = QLabel("未连接")
        self.status_label.setObjectName("StatusBig")
        layout.addWidget(self.status_label)

        self.status_hint = QLabel("填写代理地址后点击连接，流量将经 TUN 转发。")
        self.status_hint.setObjectName("StatusHint")
        self.status_hint.setWordWrap(True)
        layout.addWidget(self.status_hint)

        layout.addSpacing(4)

        micro = QLabel("PROXY URL")
        micro.setObjectName("MicroLabel")
        layout.addWidget(micro)

        self.proxy_input = QLineEdit()
        self.proxy_input.setObjectName("HeroInput")
        self.proxy_input.setPlaceholderText("socks5://127.0.0.1:1080")
        self.proxy_input.returnPressed.connect(self.toggle_proxy)
        layout.addWidget(self.proxy_input)

        # quick row
        quick = QHBoxLayout()
        quick.setSpacing(10)

        dns_wrap = QVBoxLayout()
        dns_wrap.setSpacing(4)
        dns_lbl = QLabel("DNS")
        dns_lbl.setObjectName("MicroLabel")
        self.dns_combo = QComboBox()
        self.dns_combo.addItem("Virtual", "virtual")
        self.dns_combo.addItem("Over TCP", "over-tcp")
        self.dns_combo.addItem("Direct", "direct")
        dns_wrap.addWidget(dns_lbl)
        dns_wrap.addWidget(self.dns_combo)
        quick.addLayout(dns_wrap, 1)

        addr_wrap = QVBoxLayout()
        addr_wrap.setSpacing(4)
        addr_lbl = QLabel("RESOLVER")
        addr_lbl.setObjectName("MicroLabel")
        self.dns_addr = QLineEdit()
        self.dns_addr.setPlaceholderText("8.8.8.8")
        addr_wrap.addWidget(addr_lbl)
        addr_wrap.addWidget(self.dns_addr)
        quick.addLayout(addr_wrap, 1)

        layout.addLayout(quick)

        # actions
        actions = QHBoxLayout()
        actions.setSpacing(10)
        self.btn_toggle = QPushButton("连接")
        self.btn_toggle.setObjectName("ConnectBtn")
        self.btn_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_toggle.clicked.connect(self.toggle_proxy)
        actions.addWidget(self.btn_toggle)

        self.btn_save = QPushButton("保存配置")
        self.btn_save.setObjectName("SecondaryBtn")
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save.clicked.connect(self._save_from_ui)
        actions.addWidget(self.btn_save)
        actions.addStretch()
        layout.addLayout(actions)

        return hero

    def _build_drawer(self) -> QFrame:
        self.drawer = QFrame()
        self.drawer.setObjectName("Drawer")
        self.drawer.setVisible(False)

        outer = QVBoxLayout(self.drawer)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        body = QWidget()
        layout = QVBoxLayout(body)
        layout.setContentsMargins(22, 18, 22, 18)
        layout.setSpacing(12)

        title = QLabel("设置")
        title.setObjectName("DrawerTitle")
        layout.addWidget(title)

        # bypass
        by_lbl = QLabel("BYPASS")
        by_lbl.setObjectName("MicroLabel")
        layout.addWidget(by_lbl)
        self.bypass_edit = QTextEdit()
        self.bypass_edit.setPlaceholderText("每行一个 IP / CIDR")
        self.bypass_edit.setFixedHeight(72)
        layout.addWidget(self.bypass_edit)

        # advanced grid
        adv_lbl = QLabel("ADVANCED")
        adv_lbl.setObjectName("MicroLabel")
        layout.addWidget(adv_lbl)

        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(8)

        self.verbosity = QComboBox()
        for level in ("off", "error", "warn", "info", "debug", "trace"):
            self.verbosity.addItem(level, level)
        self.chk_ipv6 = QCheckBox("启用 IPv6")

        self.tcp_timeout = QSpinBox()
        self.tcp_timeout.setRange(1, 86400)
        self.tcp_timeout.setSuffix(" s TCP")
        self.udp_timeout = QSpinBox()
        self.udp_timeout.setRange(1, 3600)
        self.udp_timeout.setSuffix(" s UDP")
        self.max_sessions = QSpinBox()
        self.max_sessions.setRange(1, 100000)
        self.max_sessions.setPrefix("sessions ")
        self.udpgw = QLineEdit()
        self.udpgw.setPlaceholderText("UdpGW  127.0.0.1:7300")

        grid.addWidget(self.verbosity, 0, 0)
        grid.addWidget(self.chk_ipv6, 0, 1)
        grid.addWidget(self.tcp_timeout, 1, 0)
        grid.addWidget(self.udp_timeout, 1, 1)
        grid.addWidget(self.max_sessions, 2, 0)
        grid.addWidget(self.udpgw, 2, 1)
        layout.addLayout(grid)

        beh_lbl = QLabel("BEHAVIOR")
        beh_lbl.setObjectName("MicroLabel")
        layout.addWidget(beh_lbl)

        self.chk_close_tray = QCheckBox("关闭窗口时最小化到托盘")
        self.chk_autostart = QCheckBox("开机自动启动")
        self.chk_start_min = QCheckBox("启动时最小化到托盘")
        self.chk_autostart.toggled.connect(self._on_autostart_toggled)
        layout.addWidget(self.chk_close_tray)
        layout.addWidget(self.chk_autostart)
        layout.addWidget(self.chk_start_min)
        layout.addStretch()

        scroll.setWidget(body)
        outer.addWidget(scroll)
        self.drawer.setMaximumHeight(320)
        return self.drawer

    def _build_console(self) -> QFrame:
        console = QFrame()
        console.setObjectName("Console")
        layout = QVBoxLayout(console)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(6)

        top = QHBoxLayout()
        title = QLabel("CONSOLE")
        title.setObjectName("ConsoleTitle")
        top.addWidget(title)
        top.addStretch()
        self.btn_clear = QPushButton("清空")
        self.btn_clear.setObjectName("ConsoleBtn")
        self.btn_clear.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_clear.clicked.connect(lambda: self.log_view.clear())
        top.addWidget(self.btn_clear)
        layout.addLayout(top)

        self.log_view = QTextEdit()
        self.log_view.setObjectName("LogView")
        self.log_view.setReadOnly(True)
        self.log_view.setFont(QFont("Consolas", 10))
        self.log_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.log_view, stretch=1)
        return console

    def _toggle_drawer(self, checked: bool) -> None:
        self.drawer.setVisible(checked)

    # ── config ──────────────────────────────────────────────

    def _load_config_to_ui(self) -> None:
        c = self._config
        self.proxy_input.setText(c.proxy_url)
        idx = self.dns_combo.findData(c.dns_strategy)
        self.dns_combo.setCurrentIndex(idx if idx >= 0 else 0)
        self.dns_addr.setText(c.dns_addr)
        self.bypass_edit.setPlainText(c.bypass_text())
        vidx = self.verbosity.findData(c.verbosity)
        self.verbosity.setCurrentIndex(vidx if vidx >= 0 else 3)
        self.chk_ipv6.setChecked(c.ipv6_enabled)
        self.tcp_timeout.setValue(c.tcp_timeout)
        self.udp_timeout.setValue(c.udp_timeout)
        self.max_sessions.setValue(c.max_sessions)
        self.udpgw.setText(c.udpgw_server)
        self.chk_close_tray.setChecked(c.close_to_tray)
        self.chk_start_min.setChecked(c.start_minimized)

    def _ui_to_config(self) -> AppConfig:
        c = self._config
        c.proxy_url = self.proxy_input.text().strip()
        c.dns_strategy = self.dns_combo.currentData()
        c.dns_addr = self.dns_addr.text().strip() or "8.8.8.8"
        c.set_bypass_text(self.bypass_edit.toPlainText())
        c.verbosity = self.verbosity.currentData()
        c.ipv6_enabled = self.chk_ipv6.isChecked()
        c.tcp_timeout = self.tcp_timeout.value()
        c.udp_timeout = self.udp_timeout.value()
        c.max_sessions = self.max_sessions.value()
        c.udpgw_server = self.udpgw.text().strip()
        c.close_to_tray = self.chk_close_tray.isChecked()
        c.autostart = self.chk_autostart.isChecked()
        c.start_minimized = self.chk_start_min.isChecked()
        return c

    def _save_from_ui(self) -> None:
        self._config = self._ui_to_config()
        save_config(self._config)
        try:
            autostart.set_enabled(self._config.autostart, minimized=self._config.start_minimized)
        except OSError as exc:
            QMessageBox.warning(self, "自启设置失败", str(exc))
        self._append_log("=== 配置已保存 ===")

    def _on_autostart_toggled(self, checked: bool) -> None:
        try:
            autostart.set_enabled(checked, minimized=self.chk_start_min.isChecked())
            self._config.autostart = checked
            save_config(self._ui_to_config())
        except OSError as exc:
            self.chk_autostart.blockSignals(True)
            self.chk_autostart.setChecked(not checked)
            self.chk_autostart.blockSignals(False)
            QMessageBox.warning(self, "自启设置失败", str(exc))

    # ── process ─────────────────────────────────────────────

    def toggle_proxy(self) -> None:
        if self._manager.is_running():
            self._manager.stop()
            return
        self._config = self._ui_to_config()
        save_config(self._config)
        error = self._manager.start(self._config)
        if error:
            QMessageBox.critical(self, "启动失败", error)
            self._append_log(f"[ERR] {error}")

    def _on_state_changed(self, state: ProxyState) -> None:
        running = state in (ProxyState.RUNNING, ProxyState.STARTING)
        copy = {
            ProxyState.STOPPED: ("未连接", "填写代理地址后点击连接，流量将经 TUN 转发。"),
            ProxyState.STARTING: ("连接中…", "正在启动 tun2proxy 进程。"),
            ProxyState.RUNNING: ("已连接", "系统流量正在通过代理隧道。"),
            ProxyState.ERROR: ("连接失败", "进程异常退出，请查看下方日志。"),
        }
        title, hint = copy.get(state, ("未知", ""))
        self.status_label.setText(title)
        self.status_hint.setText(hint)

        colors = {
            ProxyState.STOPPED: "#134e4a",
            ProxyState.STARTING: "#d97706",
            ProxyState.RUNNING: "#0891b2",  # cyan, matches logo arrow
            ProxyState.ERROR: "#e11d48",
        }
        self.status_label.setStyleSheet(
            f"font-size: 28px; font-weight: 700; letter-spacing: -0.4px; color: {colors.get(state, '#134e4a')};"
        )

        self.btn_toggle.setText("断开" if running else "连接")
        self.btn_toggle.setProperty("running", "true" if running else "false")
        self.btn_toggle.style().unpolish(self.btn_toggle)
        self.btn_toggle.style().polish(self.btn_toggle)
        self._tray.update_state(
            state,
            running=self._manager.is_running() or state == ProxyState.STARTING,
        )

    def _on_exited(self, code: int) -> None:
        if code != 0:
            self._tray.show_message("Tun2Proxy", f"进程异常退出 (code={code})")

    def _append_log(self, line: str) -> None:
        self.log_view.append(line)
        bar = self.log_view.verticalScrollBar()
        bar.setValue(bar.maximum())

    def _show_from_tray(self) -> None:
        self.showNormal()
        self.raise_()
        self.activateWindow()

    def quit_app(self) -> None:
        self._force_quit = True
        self.close()

    def closeEvent(self, event: QCloseEvent) -> None:
        if not self._force_quit and self.chk_close_tray.isChecked():
            event.ignore()
            self.hide()
            self._tray.show_message("Tun2Proxy", "已最小化到托盘，右键托盘图标可退出")
            return
        if self._manager.is_running():
            self._manager.stop()
        self._config = self._ui_to_config()
        save_config(self._config)
        self._tray.hide()
        event.accept()
        # QuitOnLastWindowClosed=False（托盘常驻），关闭窗口不会退出，需显式 quit
        QApplication.instance().quit()
