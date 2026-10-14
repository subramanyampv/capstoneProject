# Phase 4 category follow-through — 2026-10-13 America/New_York

Authored section applicability is validated and encoded as scalar Chroma category fields. The electronics restocking and FAQ sections and the footwear FAQ are scoped; general policies remain candidates for every category. Invalid scopes are quarantined; category/doc filters compose and applicable conflict evidence survives doc filters and k=1. No policy rule values, frozen labels or holdout cases changed.

Built local `policies_v2` with 28 sections using the same pinned local Voyage-4-nano weights and 2048 normalized dimensions. Changed metadata correctly requires a new index. Offline ingestion and evaluation use existing `.venv` binaries; no LLM/vendor requests were required for this update. Old retrieval and RAG artifacts remain preserved.

Validation stdout:

```text
109 passed in 6.46s
Five category filters, general exclusions and filtered k=1 conflict: passed
```

Recalibration on the same twenty development labels: raw/retained Recall@5=1.0, MRR=.90, threshold=.464133, 0/15 answerable abstentions, 5/5 unknown abstentions. See [v2 summary](retrieval/category_v2_20261013/summary.json) and [category checks](retrieval/category_v2_20261013/category_checks.json).

The category checks assert candidate applicability and exclusion preservation, not universal relevance. The broad unlabelled window/fee probe abstains for four non-electronics categories at the unchanged threshold. General window sections are still present in candidates; the specific perishable-exclusions query retains its exclusion evidence. No threshold was relaxed or new label used to hide this limitation. Electronics returns preserve both conflict sources and may exceed k.

The retrieval layer is ready for Phase 5 integration. Typed tool registration, server-derived category/product context, permissions/timeouts, specialist current-turn evidence and composer citations remain open. Human semantic calibration, untouched holdout and final-system acceptance remain later gates. Knowledge graph remains deferred. [Memory Pad](../docs/memory_pad.md) is research/backlog documentation, not runtime memory or new scope.
