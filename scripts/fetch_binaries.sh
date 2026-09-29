#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VERSION="${TUN2PROXY_VERSION:-v0.8.3}"
GITHUB_BASE="https://github.com/tun2proxy/tun2proxy/releases/download/${VERSION}"
PROXY_PREFIX="${TUN2PROXY_DOWNLOAD_PROXY-}"
PLATFORM_FILTER="${TUN2PROXY_PLATFORM:-all}"
ARCH_FILTER="${TUN2PROXY_ARCH:-all}"
TMP="${ROOT}/.tmp-bin"
BIN="${ROOT}/bin"

mkdir -p "$TMP"

download_url() {
  local zip="$1"
  if [[ -n "$PROXY_PREFIX" ]]; then
    echo "${PROXY_PREFIX%/}/${GITHUB_BASE}/${zip}"
  else
    echo "${GITHUB_BASE}/${zip}"
  fi
}

copy_bin_files() {
  local extract_dir="$1"
  local dest_rel="$2"
  local dest="${BIN}/${dest_rel}"
  mkdir -p "$dest"
  while IFS= read -r -d '' file; do
    name="$(basename "$file")"
    case "$name" in
      tun2proxy-bin|tun2proxy-bin.exe|udpgw-server|udpgw-server.exe|wintun.dll|tun2proxy.dll|tun2proxy.h|README.md)
        cp -f "$file" "${dest}/${name}"
        ;;
    esac
  done < <(find "$extract_dir" -type f -print0)

  if [[ "$dest_rel" == windows/* ]]; then
    test -f "${dest}/tun2proxy-bin.exe"
  else
    test -f "${dest}/tun2proxy-bin"
  fi
}

should_fetch() {
  local platform="$1"
  local arch="$2"
  if [[ "$PLATFORM_FILTER" != "all" && "$PLATFORM_FILTER" != "$platform" ]]; then
    return 1
  fi
  if [[ "$ARCH_FILTER" != "all" && "$ARCH_FILTER" != "$arch" ]]; then
    return 1
  fi
  return 0
}

download_one() {
  local zip="$1"
  local dest="$2"
  local platform="$3"
  local arch="$4"
  if ! should_fetch "$platform" "$arch"; then
    return 0
  fi
  local url
  url="$(download_url "$zip")"
  local zip_path="${TMP}/${zip}"
  local extract="${TMP}/${zip%.zip}"
  echo "==> ${zip} -> bin/${dest}"
  echo "    url: ${url}"
  curl -L --connect-timeout 30 --max-time 600 --retry 8 --retry-delay 3 --retry-all-errors -C - -o "$zip_path" "$url"
  local size
  size="$(wc -c < "$zip_path" | tr -d ' ')"
  if [[ "$size" -lt 100000 ]]; then
    echo "download too small ($size bytes): $zip" >&2
    exit 1
  fi
  rm -rf "$extract"
  mkdir -p "$extract"
  unzip -qo "$zip_path" -d "$extract"
  copy_bin_files "$extract" "$dest"
}

download_one "tun2proxy-x86_64-pc-windows-msvc.zip" "windows/x86_64" "windows" "x86_64"
download_one "tun2proxy-aarch64-pc-windows-msvc.zip" "windows/aarch64" "windows" "aarch64"
download_one "tun2proxy-x86_64-unknown-linux-gnu.zip" "linux/x86_64" "linux" "x86_64"
download_one "tun2proxy-aarch64-unknown-linux-gnu.zip" "linux/aarch64" "linux" "aarch64"
download_one "tun2proxy-x86_64-apple-darwin.zip" "macos/x86_64" "macos" "x86_64"
download_one "tun2proxy-aarch64-apple-darwin.zip" "macos/aarch64" "macos" "aarch64"

echo
echo "Done. Binaries under ${BIN}"
find "$BIN" -type f ! -name 'README*' | sort
