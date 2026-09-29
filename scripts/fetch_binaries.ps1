$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$Version = if ($env:TUN2PROXY_VERSION) { $env:TUN2PROXY_VERSION } else { "v0.8.3" }
$GithubBase = "https://github.com/tun2proxy/tun2proxy/releases/download/$Version"
$ProxyPrefix = if ($null -ne $env:TUN2PROXY_DOWNLOAD_PROXY) {
    $env:TUN2PROXY_DOWNLOAD_PROXY.TrimEnd("/")
} else {
    ""
}
$PlatformFilter = if ($env:TUN2PROXY_PLATFORM) { $env:TUN2PROXY_PLATFORM.ToLowerInvariant() } else { "all" }
$ArchFilter = if ($env:TUN2PROXY_ARCH) { $env:TUN2PROXY_ARCH.ToLowerInvariant() } else { "all" }
$Tmp = Join-Path $Root ".tmp-bin"
$Bin = Join-Path $Root "bin"

$Targets = @(
    @{ Zip = "tun2proxy-x86_64-pc-windows-msvc.zip"; Dest = "windows\x86_64"; Platform = "windows"; Arch = "x86_64" },
    @{ Zip = "tun2proxy-aarch64-pc-windows-msvc.zip"; Dest = "windows\aarch64"; Platform = "windows"; Arch = "aarch64" },
    @{ Zip = "tun2proxy-x86_64-unknown-linux-gnu.zip"; Dest = "linux\x86_64"; Platform = "linux"; Arch = "x86_64" },
    @{ Zip = "tun2proxy-aarch64-unknown-linux-gnu.zip"; Dest = "linux\aarch64"; Platform = "linux"; Arch = "aarch64" },
    @{ Zip = "tun2proxy-x86_64-apple-darwin.zip"; Dest = "macos\x86_64"; Platform = "macos"; Arch = "x86_64" },
    @{ Zip = "tun2proxy-aarch64-apple-darwin.zip"; Dest = "macos\aarch64"; Platform = "macos"; Arch = "aarch64" }
)

New-Item -ItemType Directory -Force -Path $Tmp | Out-Null

function Get-DownloadUrl([string]$Zip) {
    $direct = "$GithubBase/$Zip"
    if ($ProxyPrefix) {
        return "$ProxyPrefix/$direct"
    }
    return $direct
}

function Download-Zip([string]$Zip, [string]$ZipPath) {
    $url = Get-DownloadUrl $Zip
    Write-Host "    url: $url"
    & curl.exe -L --connect-timeout 30 --max-time 600 --retry 8 --retry-delay 3 --retry-all-errors -C - -o $ZipPath $url
    if ($LASTEXITCODE -ne 0) {
        throw "download failed: $Zip (exit $LASTEXITCODE)"
    }
    $len = (Get-Item $ZipPath).Length
    if ($len -lt 100000) {
        throw "download too small ($len bytes), likely not a real zip: $Zip"
    }
}

function Copy-BinFiles([string]$ExtractDir, [string]$DestRel) {
    $dest = Join-Path $Bin $DestRel
    New-Item -ItemType Directory -Force -Path $dest | Out-Null
    $names = @(
        "tun2proxy-bin.exe", "tun2proxy-bin",
        "udpgw-server.exe", "udpgw-server",
        "wintun.dll", "tun2proxy.dll", "tun2proxy.h", "README.md"
    )
    Get-ChildItem -Path $ExtractDir -Recurse -File | ForEach-Object {
        if ($names -contains $_.Name) {
            Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $dest $_.Name) -Force
        }
    }
    $binName = if ($DestRel -like "windows*") { "tun2proxy-bin.exe" } else { "tun2proxy-bin" }
    if (-not (Test-Path (Join-Path $dest $binName))) {
        throw "missing $binName after extract into $dest"
    }
}

$selected = $Targets | Where-Object {
    ($PlatformFilter -eq "all" -or $_.Platform -eq $PlatformFilter) -and
    ($ArchFilter -eq "all" -or $_.Arch -eq $ArchFilter)
}

if (-not $selected) {
    throw "no targets matched platform=$PlatformFilter arch=$ArchFilter"
}

foreach ($item in $selected) {
    $zipPath = Join-Path $Tmp $item.Zip
    $extract = Join-Path $Tmp ($item.Zip -replace '\.zip$', '')
    Write-Host "==> $($item.Zip) -> bin\$($item.Dest)"
    Download-Zip -Zip $item.Zip -ZipPath $zipPath
    if (Test-Path $extract) {
        Remove-Item -Recurse -Force $extract
    }
    Expand-Archive -Path $zipPath -DestinationPath $extract -Force
    Copy-BinFiles -ExtractDir $extract -DestRel $item.Dest
}

Write-Host ""
Write-Host "Done. Binaries under $Bin"
Get-ChildItem -Path $Bin -Recurse -File | Where-Object { $_.Name -notlike "README*" } | Select-Object FullName, Length | Format-Table -AutoSize
