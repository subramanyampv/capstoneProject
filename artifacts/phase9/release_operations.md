# Release operations measurements

Zero-model refusal/command first, then clarification, then two or more distinct result agents or escalation outcome, then one agent. Remaining model-assisted refusals are separately reported without inventing a target. Final turns only; setup/judge/warmup excluded. Nearest-rank percentiles; three concurrent case workers, serialized local embeddings. Observed samples, not production SLA.

| Path | n | p50 ms | p95 ms | Target p95 ms | Met |
|---|---:|---:|---:|---:|---|
| single_specialist | 22 | 11619.303 | 13797.005 | 30000 | True |
| multi_specialist_or_escalation | 23 | 22589.044 | 32393.051 | 45000 | True |
| clarification | 14 | 10366.532 | 12515.449 | 15000 | True |
| deterministic_refusal_or_command | 6 | 9.539 | 47.135 | 2000 | True |

Final-turn provider-reported tokens: 448777. Unavailable: endpoint price schedule not configured; token total excludes setup, judging, and usage unavailable on failed transport.

Tool errors: {'INVALID_ARGUMENT': 3, 'NOT_FOUND': 2, 'TIMEOUT': 1}. Runtime errors: {'SPECIALIST_STEP_LIMIT': 1}. These include safe negative/injected failures and do not establish semantic tool-selection accuracy. Required-tool assertions all pass in the frozen summary; broader tool correctness remains bounded by those labels.
