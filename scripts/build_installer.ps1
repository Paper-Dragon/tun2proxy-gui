param(
    [switch]$SkipBuild,
    [string]$Version = ""
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$Python = Join-Path $Root ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
    $Python = "python"
}

if (-not $Version) {
    $Version = & $Python -c "from app import __version__; print(__version__)"
    if ($LASTEXITCODE -ne 0 -or -not $Version) {
        throw "Failed to read app.__version__"
    }
    $Version = $Version.Trim()
}

$Exe = Join-Path $Root "dist\Tun2ProxyGUI\Tun2ProxyGUI.exe"
if (-not $SkipBuild -or -not (Test-Path $Exe)) {
    Write-Host "==> Building application..."
    & (Join-Path $PSScriptRoot "build.ps1")
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller build failed"
    }
}

if (-not (Test-Path $Exe)) {
    throw "Missing executable: $Exe"
}

function Find-ISCC {
    $candidates = @(
        ${env:INNOSETUP_PATH},
        (Join-Path ${env:LOCALAPPDATA} "Programs\Inno Setup 6\ISCC.exe"),
        "C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        "C:\Program Files\Inno Setup 6\ISCC.exe"
    ) | Where-Object { $_ }

    foreach ($path in $candidates) {
        if (Test-Path $path) {
            return $path
        }
    }

    $cmd = Get-Command ISCC.exe -ErrorAction SilentlyContinue
    if ($cmd) {
        return $cmd.Source
    }
    return $null
}

$ISCC = Find-ISCC
if (-not $ISCC) {
    throw "ISCC.exe not found. Install Inno Setup 6 from https://jrsoftware.org/isinfo.php or set INNOSETUP_PATH."
}

$Iss = Join-Path $Root "installer\windows\Tun2ProxyGUI.iss"
$Icon = Join-Path $Root "resources\icon.ico"
if (-not (Test-Path $Icon)) {
    Write-Host "==> Generating icon..."
    & $Python (Join-Path $Root "scripts\gen_icon.py")
}

Write-Host "==> Compiling installer (v$Version)..."
& $ISCC "/DMyAppVersion=$Version" $Iss
if ($LASTEXITCODE -ne 0) {
    throw "Inno Setup compile failed"
}

$Setup = Join-Path $Root "dist\Tun2ProxyGUI-Setup-$Version-windows-x86_64.exe"
if (-not (Test-Path $Setup)) {
    throw "Missing installer: $Setup"
}

Write-Host ""
Write-Host "Done. Installer: $Setup"
