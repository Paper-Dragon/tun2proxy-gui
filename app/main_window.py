from __future__ import annotations

import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QCloseEvent, QFont, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
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
    QStackedWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from . import __version__
from . import autostart
from .config import AppConfig, load_config, normalize_virtual_dns_pool, save_config
from .elevate import is_admin, relaunch_as_admin
from .paths import icon_path
from .process_manager import ProcessManager, ProxyState
from .styles import APP_STYLESHEET
from .tray import TrayController


class MainWindow(QWidget):
    def __init__(self, start_minimized: bool = False) -> None:
        super().__init__()
        self.setObjectName("MainWindow")
        self.setWindowTitle("Tun2Proxy GUI")
        self.resize(840, 580)
        self.setMinimumSize(740, 500)
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

    def _build_ui(self) -> None:
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_sidebar())

        content_wrapper = QWidget()
        content_layout = QVBoxLayout(content_wrapper)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(0)

        self.stack = QStackedWidget()
        self.stack.addWidget(self._build_page_dashboard())
        self.stack.addWidget(self._build_page_settings())
        self.stack.addWidget(self._build_page_logs())

        content_layout.addWidget(self.stack)
        root.addWidget(content_wrapper, 1)

    def _build_sidebar(self) -> QFrame:
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(148)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(8, 14, 8, 12)
        layout.setSpacing(8)

        brand = QHBoxLayout()
        brand.setSpacing(6)

        mark = QLabel()
        mark.setFixedSize(20, 20)
        mark.setScaledContents(True)
        icon = icon_path()
        if icon.exists():
            mark.setPixmap(QIcon(str(icon)).pixmap(20, 20))
        else:
            mark.setText("T2")
            mark.setAlignment(Qt.AlignmentFlag.AlignCenter)
        brand.addWidget(mark)

        title = QLabel("Tun2Proxy")
        title.setObjectName("BrandTitle")
        brand.addWidget(title, 1)

        layout.addLayout(brand)

        version = QLabel(f"v{__version__}")
        version.setObjectName("BrandVersion")
        layout.addWidget(version)
        layout.addSpacing(10)

        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)

        self.nav_dashboard = QPushButton("仪表盘")
        self.nav_dashboard.setObjectName("NavItem")
        self.nav_dashboard.setCheckable(True)
        self.nav_dashboard.setChecked(True)
        self.nav_dashboard.setCursor(Qt.CursorShape.PointingHandCursor)

        self.nav_settings = QPushButton("网络配置")
        self.nav_settings.setObjectName("NavItem")
        self.nav_settings.setCheckable(True)
        self.nav_settings.setCursor(Qt.CursorShape.PointingHandCursor)

        self.nav_logs = QPushButton("运行日志")
        self.nav_logs.setObjectName("NavItem")
        self.nav_logs.setCheckable(True)
        self.nav_logs.setCursor(Qt.CursorShape.PointingHandCursor)

        self.nav_group.addButton(self.nav_dashboard, 0)
        self.nav_group.addButton(self.nav_settings, 1)
        self.nav_group.addButton(self.nav_logs, 2)
        self.nav_group.idClicked.connect(self._on_nav_changed)

        layout.addWidget(self.nav_dashboard)
        layout.addWidget(self.nav_settings)
        layout.addWidget(self.nav_logs)
        layout.addStretch()

        status_box = QFrame()
        status_box.setObjectName("SidebarStatusBox")
        status_box.setCursor(Qt.CursorShape.PointingHandCursor)
        box_layout = QHBoxLayout(status_box)
        box_layout.setContentsMargins(8, 6, 8, 6)
        box_layout.setSpacing(8)

        self.sidebar_dot = QLabel("●")
        self.sidebar_dot.setObjectName("SidebarStatusDot")
        self.sidebar_dot.setStyleSheet("color: #64748b;")
        box_layout.addWidget(self.sidebar_dot)

        self.sidebar_status_text = QLabel("未连接")
        self.sidebar_status_text.setObjectName("SidebarStatusText")
        box_layout.addWidget(self.sidebar_status_text, 1)

        status_box.mousePressEvent = lambda e: self.nav_dashboard.click()

        layout.addWidget(status_box)
        return sidebar

    def _on_nav_changed(self, page_id: int) -> None:
        self.stack.setCurrentIndex(page_id)

    def _build_page_dashboard(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        self.hero_card = QFrame()
        self.hero_card.setObjectName("HeroCard")
        self.hero_card.setProperty("state", "stopped")
        hero_layout = QHBoxLayout(self.hero_card)
        hero_layout.setContentsMargins(20, 18, 20, 18)
        hero_layout.setSpacing(16)

        left_info = QVBoxLayout()
        left_info.setSpacing(6)

        badge_row = QHBoxLayout()
        badge_row.setSpacing(8)
        self.status_badge = QLabel("未连接")
        self.status_badge.setObjectName("StatusBadge")
        self.status_badge.setProperty("state", "stopped")
        badge_row.addWidget(self.status_badge)
        badge_row.addStretch()
        left_info.addLayout(badge_row)

        self.status_label = QLabel("Tun2Proxy 已就绪")
        self.status_label.setObjectName("HeroTitle")
        left_info.addWidget(self.status_label)

        self.status_hint = QLabel("填入目标代理节点地址并点击启动，系统流量将通过 TUN 虚拟网卡转发。")
        self.status_hint.setObjectName("HeroDesc")
        self.status_hint.setWordWrap(True)
        left_info.addWidget(self.status_hint)

        hero_layout.addLayout(left_info, 1)

        self.btn_toggle = QPushButton("连接代理")
        self.btn_toggle.setObjectName("HeroConnectBtn")
        self.btn_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_toggle.clicked.connect(self.toggle_proxy)
        hero_layout.addWidget(self.btn_toggle)

        layout.addWidget(self.hero_card)

        card_proxy = QFrame()
        card_proxy.setObjectName("ContentCard")
        cp_layout = QVBoxLayout(card_proxy)
        cp_layout.setContentsMargins(18, 16, 18, 16)
        cp_layout.setSpacing(14)

        card_title = QLabel("代理连接")
        card_title.setObjectName("CardTitle")
        card_desc = QLabel("配置上游代理协议、地址及 DNS 解析策略")
        card_desc.setObjectName("CardDesc")
        cp_layout.addWidget(card_title)
        cp_layout.addWidget(card_desc)

        proxy_box = QVBoxLayout()
        proxy_box.setSpacing(6)
        proxy_lbl = QLabel("上游代理地址 (URL)")
        proxy_lbl.setObjectName("FieldLabel")
        self.proxy_input = QLineEdit()
        self.proxy_input.setObjectName("MonoInput")
        self.proxy_input.setPlaceholderText("socks5://127.0.0.1:1080 或 http://127.0.0.1:7890")
        self.proxy_input.returnPressed.connect(self.toggle_proxy)
        proxy_box.addWidget(proxy_lbl)
        proxy_box.addWidget(self.proxy_input)
        cp_layout.addLayout(proxy_box)

        dns_grid = QHBoxLayout()
        dns_grid.setSpacing(12)

        dns_left = QVBoxLayout()
        dns_left.setSpacing(6)
        dns_mode_lbl = QLabel("DNS 处理模式")
        dns_mode_lbl.setObjectName("FieldLabel")
        self.dns_combo = QComboBox()
        self.dns_combo.addItem("Virtual (虚拟 DNS IP 池)", "virtual")
        self.dns_combo.addItem("Over TCP (经代理 TCP 查询)", "over-tcp")
        self.dns_combo.addItem("Direct (直连查询)", "direct")
        dns_left.addWidget(dns_mode_lbl)
        dns_left.addWidget(self.dns_combo)
        dns_grid.addLayout(dns_left, 1)

        dns_right = QVBoxLayout()
        dns_right.setSpacing(6)
        dns_server_lbl = QLabel("远程 DNS 服务器")
        dns_server_lbl.setObjectName("FieldLabel")
        self.dns_addr = QLineEdit()
        self.dns_addr.setObjectName("MonoInput")
        self.dns_addr.setPlaceholderText("8.8.8.8")
        dns_right.addWidget(dns_server_lbl)
        dns_right.addWidget(self.dns_addr)
        dns_grid.addLayout(dns_right, 1)

        cp_layout.addLayout(dns_grid)

        action_row = QHBoxLayout()
        action_row.setSpacing(10)
        self.btn_save_dashboard = QPushButton("保存配置")
        self.btn_save_dashboard.setObjectName("PrimaryBtn")
        self.btn_save_dashboard.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save_dashboard.clicked.connect(self._save_from_ui)
        action_row.addWidget(self.btn_save_dashboard)
        action_row.addStretch()
        cp_layout.addLayout(action_row)

        layout.addWidget(card_proxy)

        stat_row = QHBoxLayout()
        stat_row.setSpacing(12)

        stat_1 = QFrame()
        stat_1.setObjectName("StatMiniCard")
        s1_lay = QVBoxLayout(stat_1)
        s1_lay.setContentsMargins(12, 10, 12, 10)
        s1_lay.setSpacing(4)
        s1_title = QLabel("网络适配器")
        s1_title.setObjectName("StatMiniLabel")
        self.info_tun = QLabel("Wintun (自动)")
        self.info_tun.setObjectName("StatMiniValue")
        s1_lay.addWidget(s1_title)
        s1_lay.addWidget(self.info_tun)
        stat_row.addWidget(stat_1)

        stat_2 = QFrame()
        stat_2.setObjectName("StatMiniCard")
        s2_lay = QVBoxLayout(stat_2)
        s2_lay.setContentsMargins(12, 10, 12, 10)
        s2_lay.setSpacing(4)
        s2_title = QLabel("分流与绕过")
        s2_title.setObjectName("StatMiniLabel")
        self.info_bypass = QLabel("默认直连私网网段")
        self.info_bypass.setObjectName("StatMiniValue")
        s2_lay.addWidget(s2_title)
        s2_lay.addWidget(self.info_bypass)
        stat_row.addWidget(stat_2)

        stat_3 = QFrame()
        stat_3.setObjectName("StatMiniCard")
        s3_lay = QVBoxLayout(stat_3)
        s3_lay.setContentsMargins(12, 10, 12, 10)
        s3_lay.setSpacing(4)
        s3_title = QLabel("会话上限")
        s3_title.setObjectName("StatMiniLabel")
        self.info_sessions = QLabel("200 并发")
        self.info_sessions.setObjectName("StatMiniValue")
        s3_lay.addWidget(s3_title)
        s3_lay.addWidget(self.info_sessions)
        stat_row.addWidget(stat_3)

        layout.addLayout(stat_row)
        layout.addStretch()
        return page

    def _build_page_settings(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 16, 0)
        layout.setSpacing(14)

        card_bypass = QFrame()
        card_bypass.setObjectName("ContentCard")
        cb_lay = QVBoxLayout(card_bypass)
        cb_lay.setContentsMargins(18, 16, 18, 16)
        cb_lay.setSpacing(10)

        cb_title = QLabel("路由绕过规则 (Bypass)")
        cb_title.setObjectName("CardTitle")
        cb_desc = QLabel("指定不经过 TUN 虚拟网卡代理的 IP 地址或 CIDR 网段（每行一个）")
        cb_desc.setObjectName("CardDesc")
        cb_lay.addWidget(cb_title)
        cb_lay.addWidget(cb_desc)

        self.bypass_edit = QTextEdit()
        self.bypass_edit.setObjectName("MonoTextEdit")
        self.bypass_edit.setPlaceholderText("192.168.0.0/16\n10.0.0.0/8\n172.16.0.0/12\n127.0.0.0/8")
        self.bypass_edit.setFixedHeight(76)
        cb_lay.addWidget(self.bypass_edit)
        layout.addWidget(card_bypass)

        card_net = QFrame()
        card_net.setObjectName("ContentCard")
        cn_lay = QVBoxLayout(card_net)
        cn_lay.setContentsMargins(18, 16, 18, 16)
        cn_lay.setSpacing(12)

        cn_title = QLabel("网络核心参数")
        cn_title.setObjectName("CardTitle")
        cn_lay.addWidget(cn_title)

        grid1 = QGridLayout()
        grid1.setHorizontalSpacing(14)
        grid1.setVerticalSpacing(10)

        lbl_tun = QLabel("TUN 接口名")
        lbl_tun.setObjectName("FieldLabel")
        self.tun_name = QLineEdit()
        self.tun_name.setPlaceholderText("留空则自动生成")

        lbl_pool = QLabel("虚拟 DNS 网段池")
        lbl_pool.setObjectName("FieldLabel")
        self.virtual_dns_pool = QLineEdit()
        self.virtual_dns_pool.setObjectName("MonoInput")
        self.virtual_dns_pool.setPlaceholderText("198.18.0.0/15")

        grid1.addWidget(lbl_tun, 0, 0)
        grid1.addWidget(self.tun_name, 0, 1)
        grid1.addWidget(lbl_pool, 0, 2)
        grid1.addWidget(self.virtual_dns_pool, 0, 3)

        lbl_loglvl = QLabel("日志输出级别")
        lbl_loglvl.setObjectName("FieldLabel")
        self.verbosity = QComboBox()
        for key, label in (
            ("off", "Off (关闭)"),
            ("error", "Error (仅错误)"),
            ("warn", "Warn (警告)"),
            ("info", "Info (常规信息)"),
            ("debug", "Debug (调试)"),
            ("trace", "Trace (最详尽)"),
        ):
            self.verbosity.addItem(label, key)

        lbl_maxsess = QLabel("最大连接会话")
        lbl_maxsess.setObjectName("FieldLabel")
        self.max_sessions = QSpinBox()
        self.max_sessions.setRange(1, 100000)

        grid1.addWidget(lbl_loglvl, 1, 0)
        grid1.addWidget(self.verbosity, 1, 1)
        grid1.addWidget(lbl_maxsess, 1, 2)
        grid1.addWidget(self.max_sessions, 1, 3)

        lbl_tcpto = QLabel("TCP 超时时长")
        lbl_tcpto.setObjectName("FieldLabel")
        self.tcp_timeout = QSpinBox()
        self.tcp_timeout.setRange(1, 86400)
        self.tcp_timeout.setSuffix(" 秒")

        lbl_udpto = QLabel("UDP 超时时长")
        lbl_udpto.setObjectName("FieldLabel")
        self.udp_timeout = QSpinBox()
        self.udp_timeout.setRange(1, 3600)
        self.udp_timeout.setSuffix(" 秒")

        grid1.addWidget(lbl_tcpto, 2, 0)
        grid1.addWidget(self.tcp_timeout, 2, 1)
        grid1.addWidget(lbl_udpto, 2, 2)
        grid1.addWidget(self.udp_timeout, 2, 3)

        cn_lay.addLayout(grid1)
        layout.addWidget(card_net)

        card_udpgw = QFrame()
        card_udpgw.setObjectName("ContentCard")
        cu_lay = QVBoxLayout(card_udpgw)
        cu_lay.setContentsMargins(18, 16, 18, 16)
        cu_lay.setSpacing(12)

        cu_title = QLabel("UDP 网关设置 (UdpGW)")
        cu_title.setObjectName("CardTitle")
        cu_desc = QLabel("针对仅支持 TCP 代理协议环境转发 UDP 流量")
        cu_desc.setObjectName("CardDesc")
        cu_lay.addWidget(cu_title)
        cu_lay.addWidget(cu_desc)

        grid2 = QGridLayout()
        grid2.setHorizontalSpacing(14)
        grid2.setVerticalSpacing(10)

        lbl_udpgw = QLabel("UdpGW 服务器")
        lbl_udpgw.setObjectName("FieldLabel")
        self.udpgw = QLineEdit()
        self.udpgw.setObjectName("MonoInput")
        self.udpgw.setPlaceholderText("127.0.0.1:7300 (留空为禁用)")

        lbl_udpgw_c = QLabel("并发连接数")
        lbl_udpgw_c.setObjectName("FieldLabel")
        self.udpgw_connections = QSpinBox()
        self.udpgw_connections.setRange(1, 1000)

        lbl_udpgw_k = QLabel("保活心跳间隔")
        lbl_udpgw_k.setObjectName("FieldLabel")
        self.udpgw_keepalive = QSpinBox()
        self.udpgw_keepalive.setRange(1, 3600)
        self.udpgw_keepalive.setSuffix(" 秒")

        grid2.addWidget(lbl_udpgw, 0, 0)
        grid2.addWidget(self.udpgw, 0, 1, 1, 3)
        grid2.addWidget(lbl_udpgw_c, 1, 0)
        grid2.addWidget(self.udpgw_connections, 1, 1)
        grid2.addWidget(lbl_udpgw_k, 1, 2)
        grid2.addWidget(self.udpgw_keepalive, 1, 3)

        cu_lay.addLayout(grid2)
        layout.addWidget(card_udpgw)

        card_pref = QFrame()
        card_pref.setObjectName("ContentCard")
        cp_lay = QVBoxLayout(card_pref)
        cp_lay.setContentsMargins(18, 16, 18, 16)
        cp_lay.setSpacing(12)

        cp_title = QLabel("系统集成与常规偏好")
        cp_title.setObjectName("CardTitle")
        cp_lay.addWidget(cp_title)

        grid3 = QGridLayout()
        grid3.setHorizontalSpacing(24)
        grid3.setVerticalSpacing(10)

        self.chk_ipv6 = QCheckBox("启用 IPv6 支持")
        self.chk_exit_fatal = QCheckBox("遇到致命错误时自动退出")
        self.chk_close_tray = QCheckBox("关闭窗口时最小化到系统托盘")
        self.chk_autostart = QCheckBox("开机自动启动")
        self.chk_start_min = QCheckBox("启动时直接最小化到托盘")

        self.chk_autostart.toggled.connect(self._on_autostart_toggled)

        grid3.addWidget(self.chk_ipv6, 0, 0)
        grid3.addWidget(self.chk_exit_fatal, 0, 1)
        grid3.addWidget(self.chk_close_tray, 1, 0)
        grid3.addWidget(self.chk_autostart, 1, 1)
        grid3.addWidget(self.chk_start_min, 2, 0)

        cp_lay.addLayout(grid3)
        layout.addWidget(card_pref)

        save_bar = QHBoxLayout()
        save_bar.setSpacing(10)
        self.btn_save_settings = QPushButton("应用并保存所有设置")
        self.btn_save_settings.setObjectName("PrimaryBtn")
        self.btn_save_settings.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save_settings.clicked.connect(self._save_from_ui)
        save_bar.addWidget(self.btn_save_settings)
        save_bar.addStretch()
        layout.addLayout(save_bar)

        scroll.setWidget(page)
        return scroll

    def _build_page_logs(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        top = QHBoxLayout()
        top.setSpacing(8)

        log_title = QLabel("实时输出")
        log_title.setObjectName("CardTitle")
        top.addWidget(log_title)
        top.addStretch()

        self.btn_clear_log = QPushButton("清空日志")
        self.btn_clear_log.setObjectName("SmallBtn")
        self.btn_clear_log.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_clear_log.clicked.connect(lambda: self.log_view.clear())
        top.addWidget(self.btn_clear_log)

        self.btn_copy_log = QPushButton("复制全部")
        self.btn_copy_log.setObjectName("SmallBtn")
        self.btn_copy_log.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_copy_log.clicked.connect(self._copy_all_logs)
        top.addWidget(self.btn_copy_log)

        layout.addLayout(top)

        term_frame = QFrame()
        term_frame.setObjectName("LogTerminalFrame")
        tf_layout = QVBoxLayout(term_frame)
        tf_layout.setContentsMargins(4, 4, 4, 4)

        self.log_view = QTextEdit()
        self.log_view.setObjectName("LogTerminalView")
        self.log_view.setReadOnly(True)
        self.log_view.setFont(QFont("Cascadia Mono", 8))
        self.log_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        tf_layout.addWidget(self.log_view)

        layout.addWidget(term_frame, 1)
        return page

    def _copy_all_logs(self) -> None:
        text = self.log_view.toPlainText()
        if text:
            QApplication.clipboard().setText(text)

    def _load_config_to_ui(self) -> None:
        c = self._config
        self.proxy_input.setText(c.proxy_url)
        idx = self.dns_combo.findData(c.dns_strategy)
        self.dns_combo.setCurrentIndex(idx if idx >= 0 else 0)
        self.dns_addr.setText(c.dns_addr)
        self.bypass_edit.setPlainText(c.bypass_text())
        self.tun_name.setText(c.tun)
        self.virtual_dns_pool.setText(c.virtual_dns_pool)
        vidx = self.verbosity.findData(c.verbosity)
        self.verbosity.setCurrentIndex(vidx if vidx >= 0 else 3)
        self.chk_ipv6.setChecked(c.ipv6_enabled)
        self.chk_exit_fatal.setChecked(c.exit_on_fatal_error)
        self.tcp_timeout.setValue(c.tcp_timeout)
        self.udp_timeout.setValue(c.udp_timeout)
        self.max_sessions.setValue(c.max_sessions)
        self.udpgw.setText(c.udpgw_server)
        self.udpgw_connections.setValue(c.udpgw_connections)
        self.udpgw_keepalive.setValue(c.udpgw_keepalive)
        self.chk_close_tray.setChecked(c.close_to_tray)
        self.chk_start_min.setChecked(c.start_minimized)
        self._update_stat_summaries(c)

    def _update_stat_summaries(self, c: AppConfig) -> None:
        self.info_tun.setText(c.tun if c.tun else "Wintun (自动)")
        count = len(c.bypass)
        if count == 0:
            self.info_bypass.setText("全局接管 (无绕过)")
        else:
            self.info_bypass.setText(f"{count} 个绕过网段")
        self.info_sessions.setText(f"{c.max_sessions} 并发会话")

    def _ui_to_config(self) -> AppConfig:
        c = self._config
        c.proxy_url = self.proxy_input.text().strip()
        c.dns_strategy = self.dns_combo.currentData()
        c.dns_addr = self.dns_addr.text().strip() or "8.8.8.8"
        c.set_bypass_text(self.bypass_edit.toPlainText())
        c.tun = self.tun_name.text().strip()
        c.virtual_dns_pool = normalize_virtual_dns_pool(self.virtual_dns_pool.text())
        self.virtual_dns_pool.setText(c.virtual_dns_pool)
        c.verbosity = self.verbosity.currentData()
        c.ipv6_enabled = self.chk_ipv6.isChecked()
        c.exit_on_fatal_error = self.chk_exit_fatal.isChecked()
        c.tcp_timeout = self.tcp_timeout.value()
        c.udp_timeout = self.udp_timeout.value()
        c.max_sessions = self.max_sessions.value()
        c.udpgw_server = self.udpgw.text().strip()
        c.udpgw_connections = self.udpgw_connections.value()
        c.udpgw_keepalive = self.udpgw_keepalive.value()
        c.close_to_tray = self.chk_close_tray.isChecked()
        c.autostart = self.chk_autostart.isChecked()
        c.start_minimized = self.chk_start_min.isChecked()
        return c

    def _save_from_ui(self) -> None:
        try:
            self._config = self._ui_to_config()
        except ValueError as exc:
            QMessageBox.warning(self, "配置无效", str(exc))
            return
        save_config(self._config)
        self._update_stat_summaries(self._config)
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
        except ValueError as exc:
            self.chk_autostart.blockSignals(True)
            self.chk_autostart.setChecked(not checked)
            self.chk_autostart.blockSignals(False)
            QMessageBox.warning(self, "配置无效", str(exc))
        except OSError as exc:
            self.chk_autostart.blockSignals(True)
            self.chk_autostart.setChecked(not checked)
            self.chk_autostart.blockSignals(False)
            QMessageBox.warning(self, "自启设置失败", str(exc))

    def toggle_proxy(self) -> None:
        if self._manager.is_running():
            self._manager.stop()
            return
        if not is_admin() and not self._offer_elevation():
            return
        try:
            self._config = self._ui_to_config()
        except ValueError as exc:
            QMessageBox.critical(self, "启动失败", str(exc))
            self._append_log(f"[ERR] {exc}")
            return
        save_config(self._config)
        self._update_stat_summaries(self._config)
        error = self._manager.start(self._config)
        if error:
            QMessageBox.critical(self, "启动失败", error)
            self._append_log(f"[ERR] {error}")

    def _offer_elevation(self) -> bool:
        if sys.platform == "win32":
            body = (
                "启动代理需要管理员权限以创建 Wintun 网卡并配置路由。\n\n"
                "是否以管理员身份重新启动？"
            )
            fail_hint = "请手动右键「以管理员身份运行」。"
        elif sys.platform == "darwin":
            body = (
                "启动代理需要管理员权限以创建 TUN 设备并配置路由。\n\n"
                "是否输入密码以提升权限后重新启动？"
            )
            fail_hint = "请使用管理员密码手动启动。"
        else:
            body = (
                "启动代理需要 root 权限以创建 TUN 设备并配置路由。\n\n"
                "是否以提升权限重新启动？"
            )
            fail_hint = "请使用 sudo / pkexec 手动启动。"

        reply = QMessageBox.question(
            self,
            "需要管理员权限",
            body,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )
        if reply != QMessageBox.StandardButton.Yes:
            self._append_log("[ERR] 已取消：当前未以提升权限运行，无法启动代理")
            return False
        if relaunch_as_admin():
            QApplication.instance().quit()
            return False
        QMessageBox.critical(self, "提权失败", f"无法以提升权限启动。{fail_hint}")
        self._append_log(f"[ERR] 提权失败。{fail_hint}")
        return False

    def _on_state_changed(self, state: ProxyState) -> None:
        running = state in (ProxyState.RUNNING, ProxyState.STARTING)
        data = {
            ProxyState.STOPPED: (
                "stopped",
                "未连接",
                "Tun2Proxy 已就绪",
                "填入目标代理节点地址并点击启动，系统流量将通过 TUN 虚拟网卡转发。",
                "#64748b",
            ),
            ProxyState.STARTING: (
                "starting",
                "正在连接...",
                "正在建立代理连接",
                "正在初始化 Wintun 网卡并注入路由表规则...",
                "#d97706",
            ),
            ProxyState.RUNNING: (
                "running",
                "已连接",
                "代理隧道已建立",
                "所有系统网络流量正通过 TUN 虚拟设备分流转发。",
                "#16a34a",
            ),
            ProxyState.ERROR: (
                "error",
                "连接失败",
                "代理进程异常退出",
                "TUN 进程发生异常，请前往「运行日志」页面排查详细错误信息。",
                "#dc2626",
            ),
        }
        state_key, badge_text, title, desc, dot_color = data.get(
            state,
            ("stopped", "未知", "状态未知", "", "#64748b"),
        )

        self.hero_card.setProperty("state", state_key)
        self.hero_card.style().unpolish(self.hero_card)
        self.hero_card.style().polish(self.hero_card)

        self.status_badge.setText(badge_text)
        self.status_badge.setProperty("state", state_key)
        self.status_badge.style().unpolish(self.status_badge)
        self.status_badge.style().polish(self.status_badge)

        self.status_label.setText(title)
        self.status_hint.setText(desc)

        self.sidebar_dot.setStyleSheet(f"color: {dot_color}; font-size: 10px;")
        self.sidebar_status_text.setText(badge_text)

        self.btn_toggle.setText("断开连接" if running else "连接代理")
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
        QApplication.instance().quit()
