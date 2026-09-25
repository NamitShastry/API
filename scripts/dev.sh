#!/usr/bin/env bash
set -e

echo "============================================================"
echo " Starting AeroIndex / FareOS — Mission Control Platform     "
echo "============================================================"

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "[1/2] Starting Web Server on port 3000..."
cd "$PROJECT_ROOT/services/web"
node server.js &
WEB_PID=$!

echo "[2/2] Web Mission Control running (PID: $WEB_PID) at http://localhost:3000"
echo "Press Ctrl+C to terminate."

trap "kill $WEB_PID 2>/dev/null || true; exit 0" SIGINT SIGTERM EXIT
wait
