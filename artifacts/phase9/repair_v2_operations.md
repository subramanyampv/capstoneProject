# Repaired candidate operations

Zero-model refusal/command, then clarification, then two or more distinct result agents or escalation, then one specialist; other paths unassigned. Final turns only, nearest-rank percentiles. Three case workers with serialized embeddings and concurrent judging; setup/warmup/judges excluded. Not production SLA.

| Path | n | p50 ms | p95 ms | Target ms | Met |
|---|---:|---:|---:|---:|---|
| single_specialist | 22 | 11117.822 | 18136.887 | 30000 | True |
| multi_specialist_or_escalation | 23 | 24870.139 | 34797.654 | 45000 | True |
| clarification | 14 | 11269.514 | 13234.228 | 15000 | True |
| deterministic_refusal_or_command | 6 | 9.89 | 32.102 | 2000 | True |

Final-turn tokens: 466151. Unavailable: endpoint pricing not configured; setup/judging/failed transport usage separate.

Tool errors: {'INVALID_ARGUMENT': 7, 'NOT_FOUND': 2, 'TIMEOUT': 1}; runtime errors: {'SPECIALIST_STEP_LIMIT': 1}. These include intentional/negative failure paths and do not measure independent semantic tool-selection correctness.
