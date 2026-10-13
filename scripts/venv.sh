#!/usr/bin/env bash
# Source this helper from scripts after changing to the project root.
if [[ ! -x .venv/bin/python ]]; then
  echo "error: local .venv/bin/python is required; obtain approval before creating a venv" >&2
  exit 1
fi
PY="$(pwd)/.venv/bin/python"
export PYTHONPATH=src
