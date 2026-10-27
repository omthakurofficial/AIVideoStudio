#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "=== 1/4 Setting up Python virtual environment (.venv) ==="
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.lock.txt

echo "=== 2/4 Installing EffectCraft & FilmCraft portable binaries ==="
.venv/bin/python scripts/install_tools.py

echo "=== 3/4 Installing Next.js frontend dependencies (apps/web) ==="
pnpm --dir apps/web install --frozen-lockfile || pnpm --dir apps/web install

echo "=== 4/4 Verifying MCP engine handshakes & environment ==="
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
  cp .env.example .env
fi
.venv/bin/python scripts/mcp_probe.py
echo "Linux setup complete! Start AIVideoStudio with: .venv/bin/python scripts/dev.py"
