# Locked repair operations

Final turns only, nearest-rank percentiles. Three case workers with serialized embeddings; DeepEval judging began after this full run. Separate offline-test/hosted-readback activity may affect host latency. Setup/warmup/judging excluded. Group zero-model refusal/command paths first, then clarification, then multiple distinct result agents or escalation, then one specialist. Not production SLA.

| Path | n | p50 ms | p95 ms | Target ms | p95 target met |
|---|---:|---:|---:|---:|---|
| single_specialist | 22 | 10782.53 | 16984.415 | 30000 | True |
| multi_specialist_or_escalation | 25 | 22957.443 | 31629.689 | 45000 | True |
| clarification | 12 | 10469.917 | 13299.517 | 15000 | True |
| deterministic_refusal_or_command | 6 | 11.533 | 36.576 | 2000 | True |

Final-turn provider tokens: 471325

Tool errors: {"INVALID_ARGUMENT": 7, "NOT_FOUND": 2, "TIMEOUT": 1, "UNEXPECTED_ORDER": 1}

Runtime errors: {"SPECIALIST_STEP_LIMIT": 1, "O2_AUTHORITATIVE_CITATION:refund_policy": 1, "SPECIALIST_model_unavailable": 1}

Unavailable: endpoint pricing not configured; setup/judging/failed transport usage separate.
