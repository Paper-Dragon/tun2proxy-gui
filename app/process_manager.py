"""Manage the tun2proxy-bin.exe child process."""

from __future__ import annotations

import re
from enum import Enum

from PySide6.QtCore import QObject, QProcess, Signal

from .config import AppConfig
from .paths import bin_dir, tun2proxy_exe

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")


class ProxyState(Enum):
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    ERROR = "error"


def strip_ansi(text: str) -> str:
    return _ANSI_RE.sub("", text)


def validate_proxy_url(url: str) -> str | None:
    """Return an error message if invalid, else None."""
    value = url.strip()
    if not value:
        return "请输入代理地址"
    lowered = value.lower()
    if not (
        lowered.startswith("socks5://")
        or lowered.startswith("socks4://")
        or lowered.startswith("socks4a://")
        or lowered.startswith("http://")
        or lowered.startswith("https://")
    ):
        return "代理地址需以 socks5://、socks4://、socks4a:// 或 http:// 开头"
    # Require host:port after scheme (allow userinfo)
    rest = value.split("://", 1)[1]
    if "@" in rest:
        rest = rest.rsplit("@", 1)[-1]
    if ":" not in rest or not rest.rsplit(":", 1)[-1].isdigit():
        return "代理地址格式应为 proto://[user:pass@]host:port"
    return None


class ProcessManager(QObject):
    state_changed = Signal(object)  # ProxyState
    log_line = Signal(str)
    exited = Signal(int)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._process: QProcess | None = None
        self._state = ProxyState.STOPPED

    @property
    def state(self) -> ProxyState:
        return self._state

    def is_running(self) -> bool:
        return self._process is not None and self._process.state() == QProcess.ProcessState.Running

    def _set_state(self, state: ProxyState) -> None:
        if self._state != state:
            self._state = state
            self.state_changed.emit(state)

    def start(self, config: AppConfig) -> str | None:
        """Start tun2proxy. Returns error string on failure."""
        if self.is_running():
            return "代理已在运行"

        err = validate_proxy_url(config.proxy_url)
        if err:
            return err

        exe = tun2proxy_exe()
        if not exe.exists():
            return f"找不到 tun2proxy 可执行文件:\n{exe}"

        workdir = bin_dir()
        if not workdir.exists():
            return f"找不到 bin 目录:\n{workdir}"

        self._process = QProcess(self)
        self._process.setWorkingDirectory(str(workdir))
        self._process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self._process.readyReadStandardOutput.connect(self._on_stdout)
        self._process.readyReadStandardError.connect(self._on_stderr)
        self._process.started.connect(self._on_started)
        self._process.finished.connect(self._on_finished)
        self._process.errorOccurred.connect(self._on_error)

        args = config.to_cli_args()
        self._set_state(ProxyState.STARTING)
        self.log_line.emit(f"=== 启动: {exe.name} {' '.join(args)} ===")
        self._process.start(str(exe), args)
        return None

    def stop(self, timeout_ms: int = 3000) -> None:
        if not self._process:
            self._set_state(ProxyState.STOPPED)
            return
        if self._process.state() == QProcess.ProcessState.Running:
            self.log_line.emit("=== 正在停止进程 ===")
            self._process.terminate()
            if not self._process.waitForFinished(timeout_ms):
                self.log_line.emit("=== 强制结束进程 ===")
                self._process.kill()
                self._process.waitForFinished(2000)
        self._process = None
        self._set_state(ProxyState.STOPPED)
        self.log_line.emit("=== 进程已停止 ===")

    def _on_started(self) -> None:
        self._set_state(ProxyState.RUNNING)
        self.log_line.emit("=== 进程已启动 ===")

    def _on_finished(self, exit_code: int, _status: QProcess.ExitStatus) -> None:
        self.log_line.emit(f"=== 进程退出，状态码: {exit_code} ===")
        self._process = None
        if exit_code == 0:
            self._set_state(ProxyState.STOPPED)
        else:
            self._set_state(ProxyState.ERROR)
        self.exited.emit(exit_code)

    def _on_error(self, error: QProcess.ProcessError) -> None:
        msg = self._process.errorString() if self._process else error.name
        self.log_line.emit(f"[ERR] 进程错误: {error.name} — {msg}")
        if error == QProcess.ProcessError.FailedToStart:
            self._process = None
            self._set_state(ProxyState.ERROR)

    def _emit_output(self, prefix: str, raw: bytes) -> None:
        text = strip_ansi(raw.decode("utf-8", errors="replace"))
        for line in text.splitlines():
            line = line.strip()
            if line:
                self.log_line.emit(f"{prefix} {line}")

    def _on_stdout(self) -> None:
        if self._process:
            self._emit_output("[OUT]", bytes(self._process.readAllStandardOutput()))

    def _on_stderr(self) -> None:
        if self._process:
            self._emit_output("[ERR]", bytes(self._process.readAllStandardError()))
