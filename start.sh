#!/usr/bin/env bash
# One-command startup for the Executive Productivity Agent
# Usage: ./start.sh
# Requirements: Python 3.9+, Node 18+

set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

CYAN='\033[0;36m'
GREEN='\033[0;32m'
RED='\033[0;31m'
RESET='\033[0m'

echo ""
echo -e "  ${CYAN}Executive Productivity Agent${RESET}"
echo "  ─────────────────────────────────────"
echo ""

# ── Checks ────────────────────────────────────────────────────────────────────
if ! command -v python3 &>/dev/null; then
  echo -e "  ${RED}ERROR:${RESET} python3 not found. Install Python 3.9+ first."
  exit 1
fi

if ! command -v node &>/dev/null; then
  echo -e "  ${RED}ERROR:${RESET} node not found. Install Node 18+ first."
  exit 1
fi

if [ ! -f "$ROOT/backend/.env" ]; then
  echo -e "  ${RED}ERROR:${RESET} backend/.env not found."
  echo "  Create it with:"
  echo "    GROQ_API_KEY=your_key_here"
  echo "    GROQ_MODEL=qwen/qwen3.8-27b"
  exit 1
fi

# ── Backend ───────────────────────────────────────────────────────────────────
echo "  [1/3] Setting up Python environment…"
VENV="$ROOT/backend/.venv"

if [ ! -d "$VENV" ]; then
  python3 -m venv "$VENV"
  echo "        Created virtualenv at backend/.venv"
fi

# Activate and install deps
source "$VENV/bin/activate"
pip install -r "$ROOT/backend/requirements.txt" -q --upgrade

echo "  [2/3] Starting backend (FastAPI on :8000)…"
cd "$ROOT/backend"
uvicorn app.main:app --reload --port 8000 --log-level warning &
BACKEND_PID=$!

# Wait for backend to be ready
echo -n "        Waiting for backend"
for i in {1..15}; do
  sleep 0.5
  if curl -sf http://localhost:8000/ >/dev/null 2>&1; then
    echo -e " ${GREEN}ready${RESET}"
    break
  fi
  echo -n "."
done

# ── Frontend ──────────────────────────────────────────────────────────────────
echo "  [3/3] Starting frontend (Vite on :5173)…"
cd "$ROOT/frontend"

if [ ! -d "node_modules" ]; then
  echo "        Installing npm packages…"
  npm install --silent
fi

npm run dev -- --host &
FRONTEND_PID=$!

sleep 2

echo ""
echo -e "  ${GREEN}✓${RESET} App is running:    ${CYAN}http://localhost:5173${RESET}"
echo -e "  ${GREEN}✓${RESET} API docs at:       ${CYAN}http://localhost:8000/docs${RESET}"
echo ""
echo "  Press Ctrl+C to stop both servers."
echo ""

# Cleanup on exit
cleanup() {
  echo ""
  echo "  Stopping servers…"
  kill "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true
  deactivate 2>/dev/null || true
  echo "  Stopped."
}
trap cleanup EXIT INT TERM

wait
