#!/usr/bin/env bash
# Launch the IRP Tabletop prototype. Mac/Linux.
set -e
cd "$(dirname "$0")"

# Load .env if present (so ANTHROPIC_API_KEY is available without pasting it).
if [ -f .env ]; then
  set -a
  . ./.env
  set +a
fi

# Pick a python that exists.
PY=python3
command -v "$PY" >/dev/null 2>&1 || PY=python

echo "Starting the IRP Tabletop prototype… your browser will open shortly."
exec "$PY" -m streamlit run Home.py
