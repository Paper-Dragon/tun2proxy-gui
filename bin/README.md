官方 tun2proxy 二进制按「系统 + 架构」存放：

```
bin/
  windows/x86_64/
  windows/aarch64/
  linux/x86_64/
  linux/aarch64/
  macos/x86_64/
  macos/aarch64/
```

当前版本对应上游 release：`v0.8.3`。

更新或重新拉取：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\fetch_binaries.ps1
```

```bash
bash ./scripts/fetch_binaries.sh
```

可选环境变量：

| 变量 | 说明 |
|------|------|
| `TUN2PROXY_VERSION` | 默认 `v0.8.3` |
| `TUN2PROXY_DOWNLOAD_PROXY` | 下载代理前缀，默认 `https://ghproxy.net`；直连可设为空 |

GUI 会按当前 OS / CPU 自动选择目录；也兼容旧扁平路径 `bin/tun2proxy-bin[.exe]`。
