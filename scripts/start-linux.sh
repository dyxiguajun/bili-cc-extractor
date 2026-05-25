#!/usr/bin/env bash

set -e

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
APP_DIR="$ROOT_DIR/backend"
VENV_DIR="$APP_DIR/.venv"
HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8000}"
URL="http://$HOST:$PORT/"

echo
echo "Starting Bili CC Extractor Tools on Linux..."

cd "$APP_DIR" || {
  echo "[ERROR] backend folder not found: $APP_DIR"
  exit 1
}

if command -v python3.12 >/dev/null 2>&1; then
  PYTHON_BIN="python3.12"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="python3"
else
  echo "[ERROR] Python 3 not found."
  exit 1
fi

if [ ! -f "$VENV_DIR/bin/python" ]; then
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

xdg-open "$URL" >/dev/null 2>&1 || true
python -m uvicorn app:app --host "$HOST" --port "$PORT"
