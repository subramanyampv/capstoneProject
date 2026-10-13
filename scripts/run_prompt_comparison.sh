#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
source scripts/venv.sh
"$PY" -m capstone_agent.main compare-prompts "$@"
