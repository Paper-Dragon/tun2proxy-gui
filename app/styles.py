from __future__ import annotations

from .paths import resource_root


def get_app_stylesheet() -> str:
    res = resource_root()
    check_svg = (res / "check.svg").as_posix()
    down_svg = (res / "chevron-down.svg").as_posix()
    up_svg = (res / "chevron-up.svg").as_posix()

    return f"""
* {{
    font-family: "Segoe UI Variable Text", "Segoe UI", "Microsoft YaHei UI", -apple-system, sans-serif;
    outline: none;
}}

QWidget#MainWindow {{
    background-color: #f8fafc;
    color: #0f172a;
}}

QFrame#Sidebar {{
    background-color: #ffffff;
    border: none;
    border-right: 1px solid #e2e8f0;
}}

QLabel#BrandTitle {{
    font-size: 13px;
    font-weight: 700;
    color: #0f172a;
    letter-spacing: -0.2px;
}}

QLabel#BrandVersion {{
    font-size: 10px;
    font-weight: 600;
    color: #2563eb;
    background-color: #eff6ff;
    border-radius: 4px;
    padding: 1px 5px;
    margin-left: 26px;
}}

QPushButton#NavItem {{
    background-color: transparent;
    color: #475569;
    border: none;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 600;
    text-align: left;
    padding: 8px 10px;
}}

QPushButton#NavItem:hover {{
    background-color: #f1f5f9;
    color: #0f172a;
}}

QPushButton#NavItem:checked {{
    background-color: #eff6ff;
    color: #2563eb;
    font-weight: 700;
}}

QFrame#SidebarStatusBox {{
    background-color: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
}}

QFrame#SidebarStatusBox:hover {{
    background-color: #f1f5f9;
    border-color: #cbd5e1;
}}

QLabel#SidebarStatusDot {{
    font-size: 10px;
    font-weight: 700;
}}

QLabel#SidebarStatusText {{
    font-size: 12px;
    font-weight: 600;
    color: #334155;
}}

QFrame#ContentCard {{
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
}}

QFrame#HeroCard {{
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
}}

QFrame#HeroCard[state="running"] {{
    border: 1px solid #86efac;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ffffff, stop:1 #f0fdf4);
}}

QFrame#HeroCard[state="error"] {{
    border: 1px solid #fca5a5;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ffffff, stop:1 #fef2f2);
}}

QFrame#HeroCard[state="starting"],
QFrame#HeroCard[state="stopping"] {{
    border: 1px solid #fde047;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ffffff, stop:1 #fefce8);
}}

QLabel#StatusBadge {{
    font-size: 11px;
    font-weight: 700;
    border-radius: 6px;
    padding: 3px 8px;
}}

QLabel#StatusBadge[state="stopped"] {{
    background-color: #f1f5f9;
    color: #64748b;
}}

QLabel#StatusBadge[state="starting"],
QLabel#StatusBadge[state="stopping"] {{
    background-color: #fef3c7;
    color: #b45309;
}}

QLabel#StatusBadge[state="running"] {{
    background-color: #dcfce7;
    color: #15803d;
}}

QLabel#StatusBadge[state="error"] {{
    background-color: #fee2e2;
    color: #b91c1c;
}}

QLabel#HeroTitle {{
    font-size: 19px;
    font-weight: 700;
    color: #0f172a;
    letter-spacing: -0.3px;
}}

QLabel#HeroDesc {{
    font-size: 12px;
    color: #64748b;
}}

QPushButton#HeroConnectBtn {{
    background-color: #2563eb;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 600;
    padding: 9px 22px;
    min-height: 20px;
}}

QPushButton#HeroConnectBtn:hover {{
    background-color: #1d4ed8;
}}

QPushButton#HeroConnectBtn:pressed {{
    background-color: #1e40af;
}}

QPushButton#HeroConnectBtn[running="true"] {{
    background-color: #dc2626;
}}

QPushButton#HeroConnectBtn[running="true"]:hover {{
    background-color: #b91c1c;
}}

QLabel#CardTitle {{
    font-size: 14px;
    font-weight: 700;
    color: #0f172a;
}}

QLabel#CardDesc {{
    font-size: 12px;
    color: #64748b;
}}

QLabel#FieldLabel {{
    font-size: 12px;
    font-weight: 600;
    color: #334155;
}}

QLineEdit, QComboBox, QSpinBox {{
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 5px 10px;
    font-size: 12px;
    color: #0f172a;
    min-height: 20px;
}}

QLineEdit:hover, QComboBox:hover, QSpinBox:hover {{
    border-color: #94a3b8;
}}

QLineEdit:focus, QComboBox:focus, QSpinBox:focus {{
    border: 1px solid #2563eb;
    background-color: #ffffff;
}}

QLineEdit#MonoInput {{
    font-family: "Cascadia Mono", Consolas, "Courier New", monospace;
    font-size: 12px;
}}

QComboBox {{
    padding-right: 28px;
}}

QComboBox::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 24px;
    border: none;
}}

QComboBox::down-arrow {{
    image: url("{down_svg}");
    width: 11px;
    height: 11px;
}}

QComboBox QAbstractItemView {{
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    selection-background-color: #eff6ff;
    selection-color: #1d4ed8;
    padding: 4px;
}}

QSpinBox {{
    padding-right: 22px;
}}

QSpinBox::up-button {{
    subcontrol-origin: border;
    subcontrol-position: top right;
    width: 18px;
    border-left: 1px solid #cbd5e1;
    border-bottom: 1px solid #e2e8f0;
    border-top-right-radius: 5px;
    background-color: #f8fafc;
}}

QSpinBox::up-button:hover {{
    background-color: #e2e8f0;
}}

QSpinBox::up-arrow {{
    image: url("{up_svg}");
    width: 8px;
    height: 8px;
}}

QSpinBox::down-button {{
    subcontrol-origin: border;
    subcontrol-position: bottom right;
    width: 18px;
    border-left: 1px solid #cbd5e1;
    border-bottom-right-radius: 5px;
    background-color: #f8fafc;
}}

QSpinBox::down-button:hover {{
    background-color: #e2e8f0;
}}

QSpinBox::down-arrow {{
    image: url("{down_svg}");
    width: 8px;
    height: 8px;
}}

QTextEdit, QPlainTextEdit {{
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 8px 10px;
    font-size: 12px;
    color: #0f172a;
}}

QTextEdit:focus, QPlainTextEdit:focus {{
    border: 1px solid #2563eb;
}}

QTextEdit#MonoTextEdit {{
    font-family: "Cascadia Mono", Consolas, "Courier New", monospace;
    font-size: 12px;
}}

QPushButton#PrimaryBtn {{
    background-color: #2563eb;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 600;
    padding: 7px 18px;
}}

QPushButton#PrimaryBtn:hover {{
    background-color: #1d4ed8;
}}

QPushButton#PrimaryBtn:pressed {{
    background-color: #1e40af;
}}

QPushButton#SecondaryBtn {{
    background-color: #ffffff;
    color: #334155;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 600;
    padding: 6px 14px;
}}

QPushButton#SecondaryBtn:hover {{
    background-color: #f8fafc;
    border-color: #94a3b8;
    color: #0f172a;
}}

QPushButton#SecondaryBtn:pressed {{
    background-color: #f1f5f9;
}}

QPushButton#SmallBtn {{
    background-color: #f1f5f9;
    color: #475569;
    border: 1px solid #e2e8f0;
    border-radius: 5px;
    font-size: 11px;
    font-weight: 600;
    padding: 4px 10px;
}}

QPushButton#SmallBtn:hover {{
    background-color: #e2e8f0;
    color: #0f172a;
}}

QCheckBox {{
    color: #334155;
    font-size: 12px;
    spacing: 8px;
    font-weight: 500;
}}

QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border-radius: 4px;
    border: 1px solid #cbd5e1;
    background-color: #ffffff;
}}

QCheckBox::indicator:hover {{
    border-color: #94a3b8;
}}

QCheckBox::indicator:checked {{
    background-color: #2563eb;
    border-color: #2563eb;
    image: url("{check_svg}");
}}

QFrame#LogTerminalFrame {{
    background-color: #090d16;
    border: 1px solid #1e293b;
    border-radius: 8px;
}}

QTextEdit#LogTerminalView {{
    background-color: transparent;
    border: none;
    color: #e2e8f0;
    font-family: "Cascadia Code", "Cascadia Mono", Consolas, "Courier New", monospace;
    font-size: 10px;
    line-height: 1.45;
    padding: 10px 12px;
    selection-background-color: #334155;
    selection-color: #f8fafc;
}}

QFrame#StatMiniCard {{
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 8px;
}}

QFrame#StatMiniCard:hover {{
    border-color: #cbd5e1;
}}

QLabel#StatMiniLabel {{
    font-size: 11px;
    font-weight: 600;
    color: #64748b;
}}

QLabel#StatMiniValue {{
    font-size: 13px;
    font-weight: 700;
    color: #0f172a;
}}

QScrollBar:vertical {{
    background-color: transparent;
    width: 8px;
    margin: 2px 0;
}}

QScrollBar::handle:vertical {{
    background-color: #cbd5e1;
    border-radius: 4px;
    min-height: 24px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: #94a3b8;
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: transparent;
}}

QScrollBar:horizontal {{
    background-color: transparent;
    height: 8px;
    margin: 0 2px;
}}

QScrollBar::handle:horizontal {{
    background-color: #cbd5e1;
    border-radius: 4px;
    min-width: 24px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: #94a3b8;
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0;
}}

QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
    background: transparent;
}}

QScrollArea {{
    border: none;
    background-color: transparent;
}}
"""


APP_STYLESHEET = get_app_stylesheet()
