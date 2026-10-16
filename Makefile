.PHONY: setup test ingest ui cli eval eval-retrieval verify-category compare-rag smoke-support scan-support compare-memory scan-memory
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
verify-category:
	.venv/bin/python scripts/verify_category_retrieval.py
compare-rag:
	.venv/bin/python scripts/compare_rag.py

smoke-support:
	.venv/bin/python scripts/run_phase5_smoke.py

scan-support:
	.venv/bin/python scripts/scan_support.py

compare-memory:
	.venv/bin/python scripts/compare_memory.py

scan-memory:
	.venv/bin/python scripts/scan_memory.py

compare-style:
	.venv/bin/python scripts/compare_style.py

scan-style:
	.venv/bin/python scripts/scan_style.py

support-ready:
	env HF_HUB_OFFLINE=1 .venv/bin/capstone-agent doctor --index

support-ui:
	bash scripts/run_support_ui.sh

verify-operations:
	.venv/bin/python scripts/verify_support_operations.py

verify-hosted:
	.venv/bin/python scripts/verify_hosted_tracing.py

scan-final:
	.venv/bin/python scripts/scan_final.py

# Supply reviewed development/frozen contexts in Phase 9. No implicit holdout execution.
evaluate-support:
	.venv/bin/capstone-agent evaluate-support $(ARGS)

consistency-support:
	.venv/bin/capstone-agent evaluate-support --repeats 3 $(ARGS)

.PHONY: support-ready support-ui verify-operations verify-hosted scan-final evaluate-support consistency-support compare-style scan-style
