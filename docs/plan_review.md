# Architecture v3 reconciliation — 2026-10-13

The user adopted v3 as the authority over all previous documents. `architecture_and_plan.md` is now revision 3.1, updated with measured progress and the user's clarification. The unchanged supplied v3.0 plan is preserved in `archive/v3/architecture_and_plan_supplied_20261013.md`. Earlier designs are archived, evidence is preserved, and current summaries follow v3.

Resolved now: three specialists/six tools as target; escalation-only writes; local nano/Chroma choice; seven-document scope; knowledge graph/API ETA deferred and hidden by default; ≤2,000-character experimental input; C as development default; actual comparison table and failure breakdown; history-free submission boundary.

Implementation cautions to resolve before the relevant phase:

1. **Selection versus safety.** v3 selects C despite R05/S15 failures. Record this as a development default, not final acceptance. Existing run manifests retain their original null selection.
2. **Conflict semantics.** R05 currently describes FAQ versus electronics return policy (30 vs 15 days), while the design also describes overlapping versions of one section. Author evidence supporting the actual frozen case and distinguish authority conflicts from superseded versions. A genuinely superseded version must not create a false conflict. Ordinary policy numbers must match configured rules; deliberately conflicting FAQ content must be explicitly labeled and escalated.
3. **Illustrative records.** Order 1045 and some diagram filenames are examples. Actual O-* fixtures and ownership are preserved. Footwear is not an excluded category in the configured rules; do not introduce an exclusion from an illustrative edge-case sentence.
4. **Checkpoint privacy.** A checkpointer saves full graph state, not just `messages`. Clear transient tool/evidence payloads before retaining session state; verify reset/TTL deletion rather than assuming reducers enforce retention.
5. **Budget/failure precedence.** Reserve capacity for handoff or disclose a failed handoff when hard caps prohibit it. Never exceed a budget or claim escalation without a ticket. Mandatory safety escalation cannot disappear behind clarification/refusal edges.
6. **Grounding.** Numeric occurrence matching does not establish entailment. Evaluate citations and nonnumeric policy claims too; input/record numbers must not be mistaken for policy authority.
7. **Tracing.** Keep current hidden-input fallback until masking and failure isolation are verified. Tracing failure must not fail the customer request. Do not publish raw/unverified cloud traces under a schedule cut.
8. **Submission history.** Use the existing GitHub repository and the prepared scanned history-free source archive. A new repository/name and student/author name are not required. Do not rewrite the existing repository.

The plan quotes an earlier 75-test run. The later Phase 2 closure has 85 tests; current status records subsequent counts. The supplied original is retained in the archive; revision 3.1 explicitly updates current implementation status to the recorded 98-test result. Submission target remains 2026-10-18; planned schedule entries are not automatic completion claims.

Phase 6 checkpoint follow-through (2026-10-15): [projection memory](phase6_memory.md) resolves the full-state retention hazard by keeping the working graph uncheckpointed and saving only an allowlisted projection in a separate graph. Tests inspect intermediate checkpoints/writes/blobs and prove reset, TTL and eviction remove retained versions. General semantic/canary and hosted trace acceptance remain later gates.
