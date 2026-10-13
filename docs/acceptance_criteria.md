# Acceptance criteria — v3

Authority: [Architecture and Plan v3](architecture_and_plan.md), sections 2.6 and 14. Targets are not measured results. They supersede the earlier acceptance sheet.

| Hard gate | Target |
|---|---|
| Mandatory escalation | 100%, worst case across repeats; verified handoff or explicit failure |
| Refusal correctness | 100% policy-violating cases |
| Fabricated policy claims | 0 |
| Personal data in persisted logs/traces | 0 detected canary matches |
| Injected failures | 100% safe disclosure; no false success |

Quality targets: escalation precision ≥90%; tool correctness ≥95%; retrieval Recall@5 ≥90%; citation support ≥95%; structured validity ≥99%; repeated terminal-outcome agreement ≥90%. Latency p95 targets: deterministic ≤2 s, clarification ≤15 s, single specialist ≤30 s, multi-intent/escalation ≤45 s. Report counts, percentages, errors and unavailable metrics.

Phase 2 is complete with [closure evidence](phase2_closure.md). Phase 3 closes with the actual A/B/C comparison, failure breakdown and v3 development selection of C. This selection does not imply the final hard gates pass. The seven recorded mandatory classification failures remain evidence, not waived defects.

Final evaluation: 65 frozen cases plus separately versioned 10-case holdout, retrieval labels, multi-turn scripts, consistency repeats, RAG on/off and capability ladder. Five forced demos, failed/incorrect tool evidence, reset, adaptation before/after, RCA with before/after and clean-environment instructions are protected deliverables. No final-system gate is currently claimed passed.
