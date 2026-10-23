#!/usr/bin/env bash
# Source this helper from scripts after changing to the project root.
if [[ -x .venv/bin/python ]]; then
  PY="$(pwd)/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PY="python3"
else
  echo "error: python3 or .venv/bin/python is required. Please set up a virtual environment: python3 -m venv .venv" >&2
  exit 1
fi
export PYTHONPATH=src
