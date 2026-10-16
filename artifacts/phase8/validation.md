# Phase 8 validation — 2026-10-16

The local deployment and hosted metadata-observability gates pass for the defined synthetic scope. See [operations design](../../docs/phase8_operations.md) for commands, data boundaries and limitations.

| Gate | Evidence |
|---|---|
| Existing and clean virtual environment | 204 tests in each; clean installed versions match the existing environment; no broken requirements |
| Clean source startup | CLI status/feedback, fresh 28-chunk v2 index, six doctor checks and loopback Streamlit server |
| Live operational paths | Six of six expected outcomes with tracing disabled and six of six enabled, in separate timestamped samples |
| Actual hosted hierarchy | Twelve-run answer and thirteen-run canary/failure graph trees read back with matching parents/outputs and empty inputs |
| Hosted privacy | No current configured credential or synthetic name/email/phone/address/customer/order canary in the inspected hosted payloads |
| Failure isolation | Invalid credential/access failures preserve refusal and injury-backstop outcomes and the same verified idempotent mock ticket |
| Safe startup/logging | Named checks/static error codes; unknown tools and arbitrary schema field paths cannot enter logs verbatim; rejected request is recorded without exception text |
| UI routing | Saved screenshot of the clean-install app rendering captured synthetic routing metadata |
| Operational commands | Readiness/UI startup, tracing verification, source/runtime scans, final graph recorder/DeepEval contract and repeat command |

The clean check reused the existing pinned model cache, not an existing Python site-packages directory or vector database. The first source-isolation failure found a test hardcoding `project/.venv`; it now uses the active interpreter. An initial clean-dependency run had one UI failure with no underlying detail retained by --tb=no; the complete isolated rerun passed. A failed hosted verifier report is retained because it initially compared empty `{}` versus server `null` literally; normalization now handles emptiness only.

The small path sample gives graph elapsed p50/p95 values, counters, tokens, repairs and tool failures. It does not measure a production tail distribution or independently prove semantic quality. Frozen/holdout, routing-label review, final calibrated quality metrics, combined demonstrations and acceptance remain Phase 9. No knowledge graph or real-store action was added.
