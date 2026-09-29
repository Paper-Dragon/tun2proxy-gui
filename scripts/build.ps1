# Build Tun2Proxy GUI with PyInstaller (Windows)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$Python = Join-Path $Root ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
    Write-Host "==> Creating virtual environment..."
    if (Get-Command uv -ErrorAction SilentlyContinue) {
        uv venv .venv
        uv pip install -r requirements.txt
    } else {
        python -m venv .venv
        & $Python -m pip install -r requirements.txt
    }
}

Write-Host "==> Ensuring dependencies..."
& $Python -m pip install -r requirements.txt

Write-Host "==> Ensuring icon..."
& $Python .\scripts\gen_icon.py

Write-Host "==> Cleaning previous build..."
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue dist, build

Write-Host "==> Running PyInstaller..."
& $Python -m PyInstaller --noconfirm build.spec

Write-Host ""
Write-Host "Done. Output: $Root\dist\Tun2ProxyGUI\"
Write-Host "Run: $Root\dist\Tun2ProxyGUI\Tun2ProxyGUI.exe"
