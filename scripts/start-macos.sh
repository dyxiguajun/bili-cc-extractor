#!/usr/bin/env bash

set -e

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
APP_DIR="$ROOT_DIR/backend"
VENV_DIR="$APP_DIR/.venv"
HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8000}"
URL="http://$HOST:$PORT/"

echo
echo "Starting Bili CC Extractor Tools..."

echo
echo "[1/6] Enter backend folder..."
cd "$APP_DIR" || {
  echo "[ERROR] backend folder not found: $APP_DIR"
  read -r -p "Press Enter to exit..."
  exit 1
}

echo
echo "[2/6] Check port $PORT..."
if lsof -iTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
  PID="$(lsof -tiTCP:"$PORT" -sTCP:LISTEN | head -n 1)"
  echo "[INFO] Port $PORT is already in use. PID=$PID"
  echo "       The app may already be running."
  open "$URL"
  exit 0
fi

echo
echo "[3/6] Check Python..."
if command -v python3.12 >/dev/null 2>&1; then
  PYTHON_BIN="python3.12"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="python3"
else
  echo "[ERROR] Python 3 not found."
  echo "Please install Python 3 first: https://www.python.org/downloads/macos/"
  read -r -p "Press Enter to exit..."
  exit 1
fi

echo "Using Python: $($PYTHON_BIN --version)"

echo
echo "[4/6] Ensure virtual environment..."
if [ ! -f "$VENV_DIR/bin/python" ]; then
  echo "Creating venv at $VENV_DIR ..."
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

echo
echo "[5/6] Install requirements..."
source "$VENV_DIR/bin/activate"
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo
echo "[6/6] Open browser and run server..."
open "$URL"

python -m uvicorn app:app --reload --host "$HOST" --port "$PORT"
