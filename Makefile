.PHONY: setup test ingest ui cli eval eval-retrieval compare-rag
setup:
	test -x .venv/bin/python
	.venv/bin/python -m pip install -c constraints-dev.txt -e '.[dev,eval,ui,rag]'
test:
	env DEEPEVAL_DISABLE_DOTENV=1 DEEPEVAL_TELEMETRY_OPT_OUT=YES .venv/bin/python -m pytest -q --tb=no
ingest:
	bash scripts/ingest.sh
ui:
	bash scripts/run_ui.sh
cli:
	.venv/bin/capstone-agent status
eval:
	.venv/bin/capstone-agent evaluate artifacts/prompt_runs/20261013T030651Z-b48a462e
eval-retrieval:
	.venv/bin/python scripts/evaluate_retrieval.py
compare-rag:
	.venv/bin/python scripts/compare_rag.py
