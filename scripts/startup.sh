#!/usr/bin/env bash
# Hermes Dev Studio — Server Startup Script

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "========================================================="
echo "Starting Hermes Dev Studio Server..."
echo "========================================================="

# 1. Environment file check
if [ ! -f .env ]; then
    echo "[!] Warning: .env file not found. Copying .env.example..."
    cp .env.example .env
fi

# 2. Check Docker Availability
if command -v docker &> /dev/null && docker info &> /dev/null; then
    echo "[+] Docker Daemon detected and responsive. Container execution active."
else
    echo "[!] Docker Daemon unavailable. Application-level WorkspaceGuard bounded fallback active."
fi

# 3. Start FastAPI Server via Uvicorn
PORT="${PORT:-8000}"
HOST="${HOST:-127.0.0.1}"

echo "[*] Launching Uvicorn ASGI Server on http://${HOST}:${PORT}..."
PYTHONPATH="$PROJECT_ROOT" python3 -m uvicorn server.main:app --host "$HOST" --port "$PORT" --reload &

SERVER_PID=$!
echo "$SERVER_PID" > .server.pid
echo "[+] Hermes Dev Studio running (PID: $SERVER_PID)"