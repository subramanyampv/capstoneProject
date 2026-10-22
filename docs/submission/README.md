# Customer Support Agent

Framework-based capstone demonstrating evidence-grounded support, bounded specialist tools, memory/reset, reversible response-style adaptation and verified mock escalation. All customer and commerce data are synthetic. Final acceptance is pending the [current-build Evaluation Report](docs/Evaluation_Report.md).

Assembly note: this source draft moves to the submission root as `README.md`; links below target that final location. Run commands from the package root. Use the existing project virtual environment for every Python command. If `.venv/bin/python` is absent, stop and ask the project owner for next steps; do not silently create an environment or use global Python. Python 3.12.12 is the tested development version. The full offline test suite also requires the system Git CLI: a source-snapshot test creates and commits a temporary synthetic repository. Configure that temporary test identity locally as the test does; no real project commit or remote access is required. Scanners do not require Git.

## Configure and install

1. If no private `.env` exists, copy `.env.example` to `.env`. Do not overwrite configured credentials. The template has blank assignments; fill the required chat settings before startup.
2. Follow [environment configuration](docs/Environment_Configuration.md) for required chat fields, optional judge/embedding/tracing fields, defaults and blank-value behavior. Keep exact deployment identities and keys in ignored local configuration. Process environment takes precedence over the file.
3. A fresh source copy needs an explicit embedding identity, index ingestion and retrieval calibration before support startup. Reusing an incompatible index is rejected. The recorded threshold belongs to the historical embedding configuration and is not validated for an arbitrary replacement. Remote endpoints require HTTPS and credentials; local compatible servers may omit credentials.

```bash
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pip check
.venv/bin/capstone-agent status
.venv/bin/capstone-agent doctor
.venv/bin/python scripts/check_model.py
bash scripts/ingest.sh
.venv/bin/python scripts/evaluate_retrieval.py --index-version v2 --output artifacts/retrieval/fresh_setup
.venv/bin/capstone-agent doctor --index
```

Installation uses only the existing local environment. A successful model preflight proves connectivity, not answer correctness. Ingestion and calibration can require an approved model download or configured embedding endpoint. Calibration writes a new dated/setup-specific result and updates retrieval configuration; inspect its answerable coverage and unanswerable abstentions before using the support agent. Same-set calibration is not held-out validation. Preserve historical receipts, and rerun applicable support evaluation whenever embedding identity or retrieval configuration changes.

## Run and demonstrate

```bash
.venv/bin/capstone-agent support "Track order O-1001" --customer C-100
.venv/bin/capstone-agent support --chat --customer C-100
bash scripts/run_support_ui.sh
```

The local UI binds to `http://127.0.0.1:8501`. Select the synthetic customer before asking a question. CLI and UI use the same support runtime. One-shot CLI calls cannot share process-local memory.

In interactive chat, ask “Track O-1001,” then “What about that order?” Use `/reset`, then repeat the follow-up: the system should request an explicit reference. `/quit` exits.

For controlled adaptation, ask one policy question; send `/feedback too_long` twice; ask the same question again; send `/feedback reset_style`; repeat the question. Compare actual answer length, profile version and safety outcomes. `/feedback disable` stops learning; `/forget-preferences` deletes the customer's saved style/feedback records. Concision never waives required safety disclosures.

## Verify

```bash
.venv/bin/python -m pytest -q --tb=no
.venv/bin/python scripts/evaluate_retrieval.py --output artifacts/retrieval/verification_new
.venv/bin/python scripts/verify_support_operations.py
.venv/bin/python scripts/scan_final.py
```

The automated tests are offline. Retrieval calibration loads the configured embedding backend and may download weights or call a configured endpoint; it writes new development measurements and configuration. Use a new unused output directory for each calibration to preserve original receipts, and complete calibration before freezing the candidate for evaluation. `verify_support_operations.py` makes live synthetic support requests, including a forced mock-handoff failure and privacy canaries, so run it only under the endpoint authorization for that payload. The scan checks configured secrets and known canaries; it is not a universal privacy or repository-history proof. Optional hosted trace verification uses `scripts/verify_hosted_tracing.py` after a configured trace-producing request.

Public frozen live evaluation, when separately authorized for the configured endpoint:

```bash
.venv/bin/python scripts/run_final_suite.py --contexts evaluation/phase9/frozen_contexts_v3.json --workers 1
```

This sends synthetic evaluation inputs to the configured application endpoint and records a new run. Use one worker for reproducibility; select only declared public inputs. Unopened independent holdout inputs require a separate evaluation decision. Judge configuration and isolated comparison commands are documented in [environment configuration](docs/Environment_Configuration.md).

## Deliverables and limits

- [Problem framing](docs/Problem_Framing_Document.md)
- [Engineering and product justification](docs/Engineering_And_Product_Justification.md)
- [Debugging and failure analysis](docs/Debugging_And_Failure_Analysis.md)
- [Retrieval proof and historical limitations](docs/Retrieval_Proof.md)
- [Five-scenario demo script](docs/Demo_Script.md)
- [Evaluation Report](docs/Evaluation_Report.md): pending final-build evidence reconciliation

The system provides information and creates local mock tickets. It does not execute returns, refunds or cancellations; selected customers are not authenticated real users. Current source changes invalidate earlier runtime acceptance claims. Original experimental evidence remains private; final evidence must preserve truthful build identities, failures, skipped metrics and review limitations. No ZIP or release-ready claim is produced by this draft.

The final packet requires matching complete evaluation, safety, judge, review, demo and operational receipts. Its proposed structure is presented only after the required submission rubric gates pass; creating the ZIP then requires the user's explicit archive-structure approval.
