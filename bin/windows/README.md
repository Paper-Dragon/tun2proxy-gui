本目录放置 Windows 官方二进制，按架构分子目录：

- `x86_64/`：`tun2proxy-bin.exe`、`wintun.dll` 等
- `aarch64/`：同上（ARM64 Windows）

可用仓库根目录脚本拉取：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\fetch_binaries.ps1
```
