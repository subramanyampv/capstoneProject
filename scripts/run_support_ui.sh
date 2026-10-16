#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
source scripts/venv.sh
"$PY" -m capstone_agent.main doctor --index
exec "$PY" -m streamlit run streamlit_app.py --server.address 127.0.0.1 --server.port 8501 --server.headless true --browser.gatherUsageStats false
