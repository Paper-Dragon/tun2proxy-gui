# Tun2Proxy GUI

Windows 桌面客户端，用于图形化启动和管理 [tun2proxy](https://github.com/tun2proxy/tun2proxy)。

当前版本：**1.0.0**（仅支持 Windows）

## 功能

- 配置并启动 / 停止 `tun2proxy-bin.exe`
- DNS 策略、绕过列表、日志等级等常用参数
- 配置持久化到 `%APPDATA%\tun2proxy-gui\config.json`
- 系统托盘（关闭窗口可最小化到托盘）
- 开机自启（当前用户注册表）
- 启动时请求管理员权限（创建 TUN / 路由需要）

## 开发运行

```powershell
cd e:\tun2proxy-gui
uv venv .venv
uv pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

若无 `uv`，可用：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

可选参数：

| 参数 | 说明 |
|------|------|
| `--minimized` | 启动后隐藏到托盘 |
| `--no-elevate` | 跳过管理员提权提示（调试用） |

## 打包分发

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build.ps1
```

产物目录：`dist\Tun2ProxyGUI\`，可将整个文件夹分发给用户。其中已捆绑 `bin\`（含 `tun2proxy-bin.exe`、`wintun.dll` 等）。

> 打包产物已启用 `uac_admin`，运行时会弹出 UAC。

## 使用说明

1. **以管理员身份运行**（或允许 UAC 提权）。
2. 填写代理地址，例如 `socks5://127.0.0.1:1080` 或 `http://user:pass@host:8080`。
3. 按需选择 DNS 策略（默认 Virtual / Fake-IP）并填写绕过 IP/CIDR。
4. 点击「启动代理」，日志区域可查看输出。
5. 右键托盘图标可启停或退出。

## 目录结构

```
tun2proxy-gui/
  main.py
  app/                 # GUI 与业务逻辑
  bin/                 # tun2proxy 二进制与 wintun.dll
  resources/icon.ico
  build.spec
  scripts/build.ps1
  requirements.txt
```

## 权限说明

Tun2Proxy 在 Windows 上需要管理员权限以加载 WinTun 驱动并管理系统路由。若拒绝提权，程序仍可打开界面，但启动代理通常会失败。

## 许可证

GUI 代码以本仓库为准；`bin/` 内二进制遵循 [tun2proxy](https://github.com/tun2proxy/tun2proxy) 及其依赖的许可证（含 WinTun）。
