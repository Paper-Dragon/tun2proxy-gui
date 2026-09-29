本目录放置 macOS 官方二进制，按架构分子目录：

- `x86_64/tun2proxy-bin`
- `aarch64/tun2proxy-bin`

可用仓库根目录脚本拉取：

```bash
bash ./scripts/fetch_binaries.sh
```

若被 Gatekeeper 拦截：

```bash
xattr -dr com.apple.quarantine tun2proxy-bin udpgw-server
```
