import sys
import time
from PySide6.QtCore import QProcess, Qt, QTextStream
from PySide6.QtWidgets import QLineEdit
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QTextEdit,
    QMessageBox,
    QHBoxLayout
)

class ProxyController(QWidget):
    def __init__(self):
        super().__init__()
        self.process = None
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Tun2Proxy 控制器")
        self.resize(1000, 600)
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        
        input_layout = QHBoxLayout()
        
        self.proxy_input = QLineEdit()
        self.proxy_input.setPlaceholderText("socks5://IP:端口")
        self.proxy_input.setText("socks5://36.156.191.33:62008")
        
        self.btn_toggle = QPushButton("启动代理")
        
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setStyleSheet("font-family: Consolas; font-size: 10pt;")
        
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.proxy_input)
        input_layout.addWidget(self.btn_toggle)
        
        # 主布局
        layout.addLayout(input_layout)
        layout.addWidget(self.log_view)
        self.setLayout(layout)
        
        # 信号连接
        self.btn_toggle.clicked.connect(self.toggle_process)
    
    def toggle_process(self):
        """切换代理进程状态"""
        if self.process and self.process.state() == QProcess.Running:
            # 停止进程
            self.process.terminate()
            if not self.process.waitForFinished(3000):
                self.process.kill()
            self.btn_toggle.setText("启动代理")
            self.btn_toggle.setProperty("active", False)
            self.btn_toggle.style().polish(self.btn_toggle)
            self.log_view.append("=== 进程已停止 ===")
        else:
            # 启动进程
            if self.process and self.process.state() == QProcess.Running:
                return
                
            self.process = QProcess()
            self.process.readyReadStandardOutput.connect(self.handle_stdout)
            self.process.readyReadStandardError.connect(self.handle_stderr)
            self.process.finished.connect(self.process_finished)
            
            self.process.setWorkingDirectory("bin")
            proxy_config = self.proxy_input.text().strip()
            if not proxy_config:
                QMessageBox.warning(self, "配置错误", "请输入有效的代理地址")
                return
            
            command = "./bin/tun2proxy-bin.exe"
            args = [
                "--proxy", proxy_config,
                "--dns", "direct"
            ]
            
            self.process.start(command, args)
            
            if self.process.waitForStarted():
                self.btn_toggle.setText("停止代理")
                self.btn_toggle.setProperty("active", True)
                self.btn_toggle.style().polish(self.btn_toggle)
                self.log_view.append("=== 进程已启动 ===")
            else:
                error = self.process.errorString()
                QMessageBox.critical(self, "错误",
                    f"无法启动进程\n"
                    f"错误类型: {error}\n"
                    f"工作目录: {self.process.workingDirectory()}\n"
                    f"执行命令: {self.process.program()} { ' '.join(self.process.arguments()) }")
    
    def stop_process(self):
        """停止代理进程"""
        if self.process and self.process.state() == QProcess.Running:
            self.process.terminate()
            if not self.process.waitForFinished(3000):
                self.process.kill()
            self.log_view.append("=== 进程已终止 ===")
    
    def handle_stdout(self):
        """实时处理标准输出"""
        data = bytes(self.process.readAllStandardOutput()).decode("utf-8", errors="replace").strip()
        if data:
            self.log_view.append(f"[OUT] {data}")
            # 自动滚动到底部
            scrollbar = self.log_view.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
    
    def handle_stderr(self):
        """实时处理错误输出"""
        data = bytes(self.process.readAllStandardError()).decode("utf-8", errors="replace").strip()
        if data:
            # 移除ANSI转义码并记录日志
            clean_data = data.replace("\033[31m", "").replace("\033[0m", "")
            self.log_view.append(f"[ERR] {clean_data}")
    
    def process_finished(self):
        """进程结束处理"""
        self.log_view.append(f"=== 进程退出，状态码: {self.process.exitCode()} ===")
        self.btn_toggle.setEnabled(True)
        self.btn_toggle.setText("启动代理")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProxyController()
    window.show()
    sys.exit(app.exec())
