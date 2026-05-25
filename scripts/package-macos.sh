#!/usr/bin/env bash
set -e

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VERSION_FILE="$ROOT_DIR/version.json"

if command -v python3 >/dev/null 2>&1 && [ -f "$VERSION_FILE" ]; then
  VERSION="$(VERSION_FILE="$VERSION_FILE" python3 - <<'PY'
import json
import os
with open(os.environ["VERSION_FILE"], "r", encoding="utf-8") as f:
    print(json.load(f).get("version", "dev"))
PY
)"
else
  VERSION="dev"
fi

OUT_DIR="$ROOT_DIR/dist"
TMP_DIR="$OUT_DIR/bili-cc-extractor-macos-v$VERSION"
ZIP_FILE="$OUT_DIR/bili-cc-extractor-macos-v$VERSION.zip"

rm -rf "$TMP_DIR" "$ZIP_FILE"
mkdir -p "$OUT_DIR"

rsync -av --delete \
  --exclude=".git" \
  --exclude=".venv" \
  --exclude="venv" \
  --exclude="env" \
  --exclude="__pycache__" \
  --exclude=".DS_Store" \
  --exclude="__MACOSX" \
  --exclude="logs" \
  --exclude="dist" \
  --exclude="backend/.venv" \
  --exclude="backend/.bili_cookie" \
  --exclude="backend/.bili_user.json" \
  --exclude="backend/.bili_profile.json" \
  --exclude="*.cookie" \
  --exclude="*.cookies" \
  "$ROOT_DIR/" "$TMP_DIR/"

chmod +x "$TMP_DIR/Bili CC Extractor.app/Contents/MacOS/bili-cc-extractor-launcher" 2>/dev/null || true
chmod +x "$TMP_DIR/scripts/start-macos.sh" 2>/dev/null || true
chmod +x "$TMP_DIR/Start macOS.command" 2>/dev/null || true

cd "$OUT_DIR"
ditto -c -k --keepParent "bili-cc-extractor-macos-v$VERSION" "bili-cc-extractor-macos-v$VERSION.zip"

echo "Created: $ZIP_FILE"
