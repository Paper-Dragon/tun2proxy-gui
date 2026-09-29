from __future__ import annotations

import re
import stat
import sys
from enum import Enum

from PySide6.QtCore import QCoreApplication, QElapsedTimer, QEventLoop, QObject, QProcess, QTimer, Signal

from .config import AppConfig
from .elevate import is_admin
from .paths import bin_dir, tun2proxy_bin

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")


class ProxyState(Enum):
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"


def strip_ansi(text: str) -> str:
    return _ANSI_RE.sub("", text)


def validate_proxy_url(url: str) -> str | None:
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
    rest = value.split("://", 1)[1]
    if "@" in rest:
        rest = rest.rsplit("@", 1)[-1]
    if ":" not in rest or not rest.rsplit(":", 1)[-1].isdigit():
        return "代理地址格式应为 proto://[user:pass@]host:port"
    return None


def _ensure_executable(path) -> None:
    if sys.platform == "win32":
        return
    try:
        mode = path.stat().st_mode
        if mode & stat.S_IXUSR:
            return
        path.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    except OSError:
        pass


class ProcessManager(QObject):
    state_changed = Signal(object)
    log_line = Signal(str)
    exited = Signal(int)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._process: QProcess | None = None
        self._state = ProxyState.STOPPED
        self._stopping = False
        self._completing = False
        self._kill_timer = QTimer(self)
        self._kill_timer.setSingleShot(True)
        self._kill_timer.timeout.connect(self._force_kill)

    @property
    def state(self) -> ProxyState:
        return self._state

    def is_running(self) -> bool:
        return self._process is not None and self._process.state() == QProcess.ProcessState.Running

    def is_active(self) -> bool:
        return self._process is not None or self._state in (
            ProxyState.STARTING,
            ProxyState.RUNNING,
            ProxyState.STOPPING,
        )

    def is_stopping(self) -> bool:
        return self._stopping or self._state == ProxyState.STOPPING

    def _set_state(self, state: ProxyState) -> None:
        if self._state != state:
            self._state = state
            self.state_changed.emit(state)

    def _owns(self, proc: object) -> bool:
        return proc is self._process

    def _detach_process(self, proc: QProcess) -> None:
        for signal, slot in (
            (proc.readyReadStandardOutput, self._on_stdout),
            (proc.readyReadStandardError, self._on_stderr),
            (proc.started, self._on_started),
            (proc.finished, self._on_finished),
            (proc.errorOccurred, self._on_error),
        ):
            try:
                signal.disconnect(slot)
            except (RuntimeError, TypeError):
                pass
        if self._process is proc:
            self._process = None
        proc.deleteLater()

    def _complete_stop(self) -> None:
        if self._completing:
            return
        self._completing = True
        try:
            self._kill_timer.stop()
            proc = self._process
            self._process = None
            self._stopping = False
            if proc is not None:
                self._detach_process(proc)
            self._set_state(ProxyState.STOPPED)
            self.log_line.emit("=== 进程已停止 ===")
        finally:
            self._completing = False

    def start(self, config: AppConfig) -> str | None:
        if self._stopping:
            return "正在停止代理，请稍候"
        if self._process is not None or self._state in (
            ProxyState.STARTING,
            ProxyState.RUNNING,
            ProxyState.STOPPING,
        ):
            return "代理已在运行或正在启动"

        if not is_admin():
            if sys.platform == "win32":
                return "需要管理员权限才能创建 Wintun 网卡。请以管理员身份重新启动本程序后再试。"
            if sys.platform == "darwin":
                return "需要管理员权限才能创建 TUN 设备。请重新启动本程序并在提示时输入密码。"
            return "需要 root 权限才能创建 TUN 设备。请使用 sudo / pkexec 重新启动本程序后再试。"

        err = validate_proxy_url(config.proxy_url)
        if err:
            return err

        exe = tun2proxy_bin()
        if not exe.exists():
            return f"找不到 tun2proxy 可执行文件:\n{exe}"

        workdir = exe.parent if exe.parent.exists() else bin_dir()
        if not workdir.exists():
            return f"找不到 bin 目录:\n{workdir}"

        _ensure_executable(exe)

        proc = QProcess(self)
        proc.setWorkingDirectory(str(workdir))
        proc.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        proc.readyReadStandardOutput.connect(self._on_stdout)
        proc.readyReadStandardError.connect(self._on_stderr)
        proc.started.connect(self._on_started)
        proc.finished.connect(self._on_finished)
        proc.errorOccurred.connect(self._on_error)
        self._process = proc

        args = config.to_cli_args()
        self._set_state(ProxyState.STARTING)
        self.log_line.emit(f"=== 启动: {exe.name} {' '.join(args)} ===")
        if self._process is not proc or self._stopping:
            return None
        proc.start(str(exe), args)
        return None

    def stop(self, timeout_ms: int = 3000, *, blocking: bool = False) -> None:
        if self._stopping:
            if blocking:
                self._drain_until_stopped(timeout_ms + 2000)
            return
        proc = self._process
        if proc is None:
            if self._state != ProxyState.STOPPED:
                self._set_state(ProxyState.STOPPED)
            return

        self._stopping = True
        self._set_state(ProxyState.STOPPING)

        if proc.state() == QProcess.ProcessState.NotRunning:
            self._complete_stop()
            return

        self.log_line.emit("=== 正在停止进程 ===")
        if proc.state() == QProcess.ProcessState.Starting:
            proc.kill()
        else:
            proc.terminate()
            self._kill_timer.start(timeout_ms)

        if blocking:
            self._drain_until_stopped(timeout_ms + 2000)

    def _drain_until_stopped(self, timeout_ms: int) -> None:
        elapsed = QElapsedTimer()
        elapsed.start()
        flags = QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents
        while self._process is not None and elapsed.elapsed() < timeout_ms:
            QCoreApplication.processEvents(flags, 50)
        if self._process is not None and self._stopping:
            self._force_kill()
            deadline = elapsed.elapsed() + 1000
            while self._process is not None and elapsed.elapsed() < deadline:
                QCoreApplication.processEvents(flags, 50)
        if self._process is not None and self._stopping:
            self._complete_stop()

    def _force_kill(self) -> None:
        proc = self._process
        if not self._stopping or proc is None:
            return
        if proc.state() != QProcess.ProcessState.NotRunning:
            self.log_line.emit("=== 强制结束进程 ===")
            proc.kill()

    def _on_started(self) -> None:
        if not self._owns(self.sender()) or self._stopping:
            return
        self._set_state(ProxyState.RUNNING)
        self.log_line.emit("=== 进程已启动 ===")

    def _on_finished(self, exit_code: int, _status: QProcess.ExitStatus) -> None:
        proc = self.sender()
        if not self._owns(proc):
            return
        if self._stopping:
            self._complete_stop()
            return
        self.log_line.emit(f"=== 进程退出，状态码: {exit_code} ===")
        if isinstance(proc, QProcess):
            self._detach_process(proc)
        if exit_code == 0:
            self._set_state(ProxyState.STOPPED)
        else:
            self._set_state(ProxyState.ERROR)
        self.exited.emit(exit_code)

    def _on_error(self, error: QProcess.ProcessError) -> None:
        proc = self.sender()
        if not self._owns(proc) or self._stopping:
            return
        msg = proc.errorString() if isinstance(proc, QProcess) else error.name
        self.log_line.emit(f"[ERR] 进程错误: {error.name} — {msg}")
        if error == QProcess.ProcessError.FailedToStart and isinstance(proc, QProcess):
            self._detach_process(proc)
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
