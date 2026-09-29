#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

PYTHON="${PYTHON:-python3}"
if [[ -x "$ROOT/.venv/bin/python" ]]; then
  PYTHON="$ROOT/.venv/bin/python"
fi

"$PYTHON" -m pip install -r requirements.txt
"$PYTHON" -m pip install pyinstaller
"$PYTHON" -m PyInstaller --noconfirm --clean build.spec

echo "Build output: $ROOT/dist/Tun2ProxyGUI/"
