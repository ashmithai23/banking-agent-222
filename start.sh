#!/usr/bin/env bash
# Start VectraBank backend (FastAPI :8000) and frontend (Vite :5173).
#   ./start.sh          dev mode: backend + Vite dev server with hot reload
#   ./start.sh prod     build the frontend and serve everything from FastAPI on :8000
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
MODE="${1:-dev}"
BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-5173}"

# --- backend deps
cd "$ROOT/backend"
if [ ! -d .venv ]; then
  echo ">> Creating Python virtualenv"
  python3 -m venv .venv
fi
if [ ! -f .venv/.deps-installed ] || [ requirements.txt -nt .venv/.deps-installed ]; then
  echo ">> Installing backend dependencies"
  .venv/bin/pip install -q -r requirements.txt
  touch .venv/.deps-installed
fi
[ -f .env ] || cp .env.example .env

# --- frontend deps
cd "$ROOT/frontend"
if [ ! -d node_modules ]; then
  echo ">> Installing frontend dependencies"
  npm install --no-fund --no-audit
fi

if [ "$MODE" = "prod" ]; then
  echo ">> Building frontend"
  npm run build
  cd "$ROOT/backend"
  echo ">> Serving app at http://localhost:$BACKEND_PORT"
  exec .venv/bin/uvicorn api:app --host 0.0.0.0 --port "$BACKEND_PORT"
fi

cd "$ROOT/backend"
.venv/bin/uvicorn api:app --host 0.0.0.0 --port "$BACKEND_PORT" --reload &
BACK_PID=$!
trap 'kill $BACK_PID 2>/dev/null || true' EXIT INT TERM

cd "$ROOT/frontend"
echo ">> Backend:  http://localhost:$BACKEND_PORT/docs"
echo ">> Frontend: http://localhost:$FRONTEND_PORT"
VITE_BACKEND_URL="http://localhost:$BACKEND_PORT" npx vite --port "$FRONTEND_PORT"
