$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host "=== 1/4 Setting up Python virtual environment (.venv) ==="
if (-not (Test-Path ".venv")) {
    python -m venv .venv
}
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -r requirements.lock.txt

Write-Host "=== 2/4 Installing EffectCraft & FilmCraft Windows x64 portable binaries ==="
& .\.venv\Scripts\python.exe scripts\install_tools.py --platform windows

Write-Host "=== 3/4 Installing Next.js frontend dependencies (apps\web) ==="
pnpm --dir apps/web install

Write-Host "=== 4/4 Verifying MCP engine handshakes & environment ==="
if (-not (Test-Path ".env") -and (Test-Path ".env.example")) {
    Copy-Item ".env.example" ".env"
}
& .\.venv\Scripts\python.exe scripts\mcp_probe.py
Write-Host "Windows setup complete! Start AIVideoStudio with: .\.venv\Scripts\python.exe scripts\dev.py"
