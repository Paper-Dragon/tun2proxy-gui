"""Application visual theme — aligned with tunnel logo (teal + cyan)."""

APP_STYLESHEET = """
* {
    font-family: "Segoe UI Variable Text", "Segoe UI", "Microsoft YaHei UI", sans-serif;
}

QWidget#MainWindow {
    background: #eef6f5;
    color: #0f1f1c;
}

/* —— top bar —— */
QFrame#TopBar {
    background: #ffffff;
    border: none;
    border-bottom: 1px solid #d5e8e4;
    border-radius: 0;
}

QLabel#LogoMark {
    background: transparent;
    color: #ffffff;
    border-radius: 8px;
    font-size: 12px;
    font-weight: 800;
    padding: 0;
    letter-spacing: 0.5px;
}

QLabel#AppName {
    font-size: 14px;
    font-weight: 700;
    color: #134e4a;
}

QLabel#AppMeta {
    font-size: 11px;
    color: #6b9a93;
}

QPushButton#IconBtn {
    background: transparent;
    border: 1px solid #cfe3df;
    border-radius: 8px;
    color: #134e4a;
    padding: 6px 10px;
    font-size: 12px;
    font-weight: 600;
}
QPushButton#IconBtn:hover { background: #e8f5f2; }
QPushButton#IconBtn:checked {
    background: #0f766e;
    color: #ffffff;
    border-color: #0f766e;
}

/* —— hero —— */
QFrame#Hero {
    background: #ffffff;
    border: 1px solid #d5e8e4;
    border-radius: 16px;
}

QLabel#StatusBig {
    font-size: 28px;
    font-weight: 700;
    color: #134e4a;
    letter-spacing: -0.4px;
}

QLabel#StatusHint {
    font-size: 12px;
    color: #5f8a84;
}

QLabel#MicroLabel {
    font-size: 11px;
    font-weight: 700;
    color: #7aa8a1;
    letter-spacing: 0.8px;
}

QLineEdit#HeroInput {
    background: #f3faf8;
    border: 1.5px solid #d5e8e4;
    border-radius: 12px;
    padding: 14px 16px;
    font-size: 15px;
    font-family: Consolas, "Cascadia Mono", monospace;
    color: #0f1f1c;
    selection-background-color: #0f766e;
    selection-color: #ffffff;
}
QLineEdit#HeroInput:focus {
    background: #ffffff;
    border: 1.5px solid #0f766e;
}

QPushButton#ConnectBtn {
    background: #0f766e;
    color: #ffffff;
    border: none;
    border-radius: 12px;
    padding: 14px 22px;
    font-size: 14px;
    font-weight: 700;
    min-width: 140px;
}
QPushButton#ConnectBtn:hover { background: #0d9488; }
QPushButton#ConnectBtn:pressed { background: #115e59; }
QPushButton#ConnectBtn[running="true"] {
    background: #e11d48;
}
QPushButton#ConnectBtn[running="true"]:hover {
    background: #be123c;
}

QPushButton#SecondaryBtn {
    background: #ffffff;
    color: #134e4a;
    border: 1px solid #cfe3df;
    border-radius: 12px;
    padding: 14px 16px;
    font-size: 13px;
    font-weight: 600;
}
QPushButton#SecondaryBtn:hover { background: #e8f5f2; }

QComboBox, QSpinBox, QLineEdit {
    background: #ffffff;
    border: 1px solid #d5e8e4;
    border-radius: 10px;
    padding: 8px 10px;
    font-size: 13px;
    color: #0f1f1c;
    min-height: 18px;
}
QComboBox:focus, QSpinBox:focus, QLineEdit:focus {
    border: 1px solid #0f766e;
}
QComboBox::drop-down { border: none; width: 24px; }
QComboBox QAbstractItemView {
    background: #ffffff;
    border: 1px solid #d5e8e4;
    selection-background-color: #e8f5f2;
    selection-color: #134e4a;
    outline: none;
    padding: 4px;
}

QTextEdit, QPlainTextEdit {
    background: #ffffff;
    border: 1px solid #d5e8e4;
    border-radius: 10px;
    padding: 10px;
    font-size: 12px;
    color: #0f1f1c;
}
QTextEdit:focus, QPlainTextEdit:focus {
    border: 1px solid #0f766e;
}

QCheckBox {
    color: #2d5a54;
    spacing: 8px;
    font-size: 13px;
}
QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border-radius: 4px;
    border: 1px solid #b6d4ce;
    background: #ffffff;
}
QCheckBox::indicator:checked {
    background: #0f766e;
    border-color: #0f766e;
}

/* —— settings drawer —— */
QFrame#Drawer {
    background: #ffffff;
    border: 1px solid #d5e8e4;
    border-radius: 16px;
}
QLabel#DrawerTitle {
    font-size: 13px;
    font-weight: 700;
    color: #134e4a;
}

/* —— console —— */
QFrame#Console {
    background: #071c1a;
    border: none;
    border-radius: 16px;
}
QLabel#ConsoleTitle {
    color: #5eead4;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.8px;
}
QPushButton#ConsoleBtn {
    background: transparent;
    border: none;
    color: #5f8a84;
    font-size: 11px;
    font-weight: 600;
    padding: 2px 6px;
}
QPushButton#ConsoleBtn:hover { color: #22d3ee; }

QTextEdit#LogView {
    background: transparent;
    border: none;
    color: #a7f3d0;
    font-family: Consolas, "Cascadia Mono", "Courier New", monospace;
    font-size: 12px;
    padding: 0 4px 8px 4px;
}

QScrollBar:vertical {
    background: transparent;
    width: 8px;
    margin: 2px;
}
QScrollBar::handle:vertical {
    background: #134e4a;
    border-radius: 4px;
    min-height: 24px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

QScrollArea { border: none; background: transparent; }
"""
