# Submission audit — 2026-10-18

> Historical audit snapshot. Subsequent developer remediations and current-build checks are recorded in [Submission readiness](../submission_readiness.md) and [Current status](../current_status.md). The original findings, scores and evidence below remain unchanged; they are not current-build validation.

**Decision: NOT READY. Advisory rubric score: 89/100. No ZIP created.** The user's latest instruction requires stopping before archive creation regardless of score.

Application source is unchanged. The project-root `.env.example` now contains four empty configuration keys. The private `.env` was neither opened nor changed. Reports and curated evidence are contained in this folder; existing root documents and immutable historical artifacts were preserved.

| Artifact | Purpose |
|---|---|
| [Rubric_Evaluation.md](Rubric_Evaluation.md) | Nine scored areas, evidence and deductions |
| [Structured_Remediation_Task_List.md](Structured_Remediation_Task_List.md) | Developer changes and acceptance checks |
| [Problem_Framing_Document.md](Problem_Framing_Document.md) | Persona, workflow, constraints and failure boundaries |
| [Demo_Script.md](Demo_Script.md) | Five forced interactions and saved actual responses |
| [Prompt_Comparison_Report.md](Prompt_Comparison_Report.md) | Fixed-set A/B/C experiment and RAG ablation |
| [Debugging_And_Failure_Analysis.md](Debugging_And_Failure_Analysis.md) | Unsupported numeric policy claim and fresh guard replay |
| [Engineering_And_Product_Justification.md](Engineering_And_Product_Justification.md) | Architecture, agents, memory, feedback, operations |
| [Submission_File_Selection.md](Submission_File_Selection.md) | Explicit proposed allowlist and exclusions |
| [evidence/verification_summary.json](evidence/verification_summary.json) | Fresh tests, manifest checks and saved quality metrics |
| [evidence/demo_test_logs.json](evidence/demo_test_logs.json) | Five curated actual interaction records |

Paths in reports are relative to the application root unless linked locally. Historical run identifiers remain exact provenance; historical model labels were not copied into these reports. The source supports a configurable OpenAI API-compatible chat endpoint. Retrieval is presently tied to a particular local embedding implementation; provider agnosticism is incomplete.

Fresh checks: 413 offline tests pass; 51/51 source and 65/65 build hashes match the frozen-run manifest; numeric guard accepts the recorded answer and rejects a 500-day mutation in three deterministic probes. No remote model calls, blind test execution, new environment creation, dependency installation, commit or publication occurred.

Existing acceptance ledger: `../current_status.md`. It records pending final acceptance and unseen evaluation. An AI-proxy iteration review is not actual human calibration. Confidence of 99.99% is not established by these finite development tests.
