# Knowledge and retrieval — Phase 4

Authority: [Architecture and Plan v3](architecture_and_plan.md), section 9. Initial implementation and measured evidence recorded 2026-10-13. Knowledge graph remains deferred until initial-product acceptance.

Seven versioned synthetic documents now live in `knowledge/raw/`. The corpus mirrors the frozen rule values, explicitly labels R05's contradictory FAQ electronics window, and states unknown refund-method/processing-time details rather than inventing them. Documents have ID, owner, version, authority and effective date. No frozen evaluation case or fixture was edited.

The local model is `voyageai/voyage-4-nano`, pinned to `67fabc9bef010dabc5f6024aa1b1b6b93410426f`. Documents and queries use separate model-defined input modes. CPU inference returns finite, L2-normalized 2,048-dimensional vectors. The pinned custom architecture was inspected before loading. The model cache and custom module cache stay in ignored `.cache/`. Loading the pinned local snapshot avoids an unrelated Transformers tokenizer metadata lookup and allows offline reuse. [Official model card](https://huggingface.co/voyageai/voyage-4-nano).

Chroma 1.5.9 through langchain-chroma 1.1.0 persists `policies_v1` under ignored `knowledge/index/chroma_v1`. Cosine distance is configured explicitly and telemetry is disabled. The build contains 28 whole heading sections; authored sections are bounded to 2,400 UTF-8 bytes. Larger sections fail for splitting rather than being silently truncated. Token-aware overlap splitting is unnecessary for this corpus and remains a documented extension. The manifest records model/revision/dimension/normalization, source hashes, chunking, rules and collection. Changed inputs require a new index version; incompatible or incomplete indices fail closed.

Policy search returns complete citation metadata, scores, threshold state and conflict details. It filters future and superseded sources and prefers policy authority for near-tied scores. Doc-type filtering is supported; category currently helps the explicit electronics conflict topic check rather than acting as a full category metadata filter. The declared R05 FAQ/policy conflict inserts both applicable sources deterministically; this is disclosed separately from vector retrieval quality. Overlapping retrieved versions are flagged, but broader conflicting-version corpus evaluation is future work.

## Measured retrieval: initial versus improved profile

The same 20 development labels (15 answerable, five unanswerable) are unchanged. The ten holdout cases remain untouched. The query profile `policy-context-v1` adds public catalog category hints only for policy questions, exception-topic hints, and explicit human-request hints. It does not add policy facts, customer identity or eligibility decisions. Injury-review questions are kept distinct from general representative requests. This is a small deterministic rewrite, not a knowledge graph or a model-based planner.

| Measure | Initial profile | Improved profile |
|---|---:|---:|
| Candidate Recall@5 | 100% | 100% |
| Candidate MRR | 0.90 | 0.90 |
| Threshold | 0.464133 | 0.464133 |
| Recall@5 after threshold | 80% | 100% |
| Answerable queries fully rejected | 2/15 | 0/15 |
| Unanswerable queries rejected | 5/5 | 5/5 |

The rejected TrailRunner/exception queries and lost human-request governing section are now retained on this development set. An intermediate rewrite lowered MRR to 0.867; excluding injury-review questions from general-human hints restored 0.90. None of these measurements establishes held-out generalization or final safety acceptance.

Calibration is tied to the query-profile name and source hash; a changed profile requires recalibration before default use. Both baseline and current results are retained. Metadata filters and small k cannot hide mandatory conflict sources: all applicable versions of a retained section are checked, and declared FAQ/policy conflicts retain both sides even when the filter excludes one. Mandatory conflict evidence may exceed k, with an explicit flag and a twenty-source cap. An injected source excluded from the vector search has score=null rather than a fabricated similarity score. Grounded validation requires the actual supplied conflicting references, including different versions of the same section.

[Initial baseline](../artifacts/retrieval/baseline_20261013/summary.json) · [current summary](../artifacts/retrieval/summary.json) · [CSV](../artifacts/retrieval/retrieval_eval.csv) · [relevance examples](../artifacts/retrieval/relevance_examples.json) · [index manifest](../knowledge/index_manifest.json).

## RAG on/off experiment

Ten identical frozen policy cases were run in both modes with the same model/settings and a separately versioned Phase 4 prompt derived from C. This single-agent experiment has no order tools, writes, memory or verified escalation tickets; it does not claim the Phase 5 architecture is built.

| Mode | Validated outputs | Cited outputs | Policy success status | Escalation classification |
|---|---:|---:|---:|---:|
| No RAG | 9/10 | 0/10 | 0/10 | 0/10 |
| RAG | 10/10 | 9/10 | 7/10 | 1/10 |

R05 without evidence failed output grounding validation; the failure is preserved. With RAG, the model surfaced both sources and classified escalation. This is not proof of a ticket or the final RCA guard behavior. In that initial run R01 remained insufficient evidence; the improved profile now retrieves its governing return-window section. Citation resolution and syntactic numeric screening pass for validated outputs; they do not establish semantic faithfulness or zero fabricated policy.

Evidence: [RAG run summary](../artifacts/rag_runs/20261013T203731Z/summary.json) and [all 20 outputs, including failures/repairs](../artifacts/rag_runs/20261013T203731Z/outputs.jsonl). [Same-model DeepEval faithfulness](../artifacts/rag_runs/20261013T203731Z/deepeval_faithfulness.json) measured nine context-bearing outputs: each scored 1.0. Eleven no-context outputs were skipped; no judge errors occurred. This is indicative self-evaluation, not independent validation; human calibration remains pending.

## Follow-through runs and semantic wording review

The improved-profile ten-case rerun is [20261013T223402Z](../artifacts/rag_runs/20261013T223402Z/summary.json): both modes validated 10/10; RAG cited 10/10, with eight policy-success classifications and one conflict escalation classification. No-RAG cited none and had no policy-success classification. These are experimental classifications, not verified order outcomes or tickets.

Same-model DeepEval scored nine RAG outputs at 1.0 and flagged R02 at 0.667: the wording blurred an inclusive return window with a separate refund deadline. The corpus does not define an independent refund deadline. The rejected/flagged wording is preserved, not converted into a pass. The answer prompt was revised to `phase4-rag-v2` to separate these concepts, state that the final day is included, and avoid individual eligibility decisions from unverified delivery claims. The [targeted prompt-v2 run](../artifacts/rag_runs/20261013T224043Z/summary.json) covers R01/R02/R05/R08 in both modes: four RAG outputs validated/cited and four empty-evidence outputs validated without citations. [Same-model faithfulness](../artifacts/rag_runs/20261013T224043Z/deepeval_faithfulness.json) scores all four RAG outputs at 1.0; four no-context outputs are skipped. R02 now explicitly states the inclusive return window without inventing a separate refund deadline. This is targeted indicative before/after evidence, not a complete final-system evaluation. Human calibration remains pending; a self-judge flag or score is not final proof of entailment.

Exact prompt snapshots, query-profile snapshots and query hints are preserved. The final injury-request refinement did not change any of the ten rerun inputs; equivalence is explicitly recorded rather than replacing the run's original source hash.

## Reproduce

```bash
make setup
make ingest
make eval-retrieval
.venv/bin/capstone-agent search-policy "FAQ says 30 days but electronics returns says 15 days for my speaker"
make compare-rag
.venv/bin/python scripts/judge_rag.py artifacts/rag_runs/20261013T203731Z
```

The first embedding build downloads model weights; subsequent `HF_HUB_OFFLINE=1 make ingest` uses the pinned local snapshot. Ingestion is idempotent for unchanged inputs. `make compare-rag` uses the configured hosted/local LLM and makes 20 scheduled requests plus bounded repairs/retries. Judge runs use that same model and are indicative self-evaluation; no DeepEval upload occurs. Generated model/index data are excluded from Git; manifests and sanitized evaluation evidence are retained.
