#!/usr/bin/env bash
# Hermes Dev Studio — Server Shutdown Script

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

if [ -f .server.pid ]; then
    PID=$(cat .server.pid)
    echo "[*] Stopping Hermes Dev Studio Server (PID: $PID)..."
    kill "$PID" 2>/dev/null || true
    rm -f .server.pid
    echo "[+] Server gracefully stopped."
else
    echo "[!] .server.pid file not found. Finding running Uvicorn process..."
    pkill -f "uvicorn server.main:app" || echo "[!] No running server process found."
fi