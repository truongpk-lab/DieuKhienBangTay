$ErrorActionPreference = "Stop"

$root = Resolve-Path (Join-Path $PSScriptRoot "..")
$indexPath = Join-Path $root "dist\index.html"

if (-not (Test-Path $indexPath)) {
  throw "Missing dist/index.html. Run npm run build first."
}

$browserCandidates = @(
  "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe",
  "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe",
  "$env:LOCALAPPDATA\Microsoft\Edge\Application\msedge.exe",
  "$env:ProgramFiles\Google\Chrome\Application\chrome.exe",
  "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
  "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe"
)

$browser = $browserCandidates | Where-Object { $_ -and (Test-Path $_) } | Select-Object -First 1
$appUrl = (New-Object System.Uri($indexPath)).AbsoluteUri
$profileDir = Join-Path $env:LOCALAPPDATA "ACVGestureControl\BrowserProfile"
New-Item -ItemType Directory -Force -Path $profileDir | Out-Null

if ($browser) {
  Start-Process -FilePath $browser -ArgumentList @(
    "--app=$appUrl",
    "--user-data-dir=$profileDir",
    "--no-first-run",
    "--disable-features=Translate"
  )
  exit 0
}

Start-Process -FilePath $indexPath
