# Knowledge and retrieval — Phase 4

Authority: [Architecture and Plan v3](architecture_and_plan.md), section 9. Initial implementation and measured evidence recorded 2026-10-13. Knowledge graph remains deferred until initial-product acceptance.

Seven versioned synthetic documents now live in `knowledge/raw/`. The corpus mirrors the frozen rule values, explicitly labels R05's contradictory FAQ electronics window, and states unknown refund-method/processing-time details rather than inventing them. Documents have ID, owner, version, authority and effective date. No frozen evaluation case or fixture was edited.

The local model is `voyageai/voyage-4-nano`, pinned to `67fabc9bef010dabc5f6024aa1b1b6b93410426f`. Documents and queries use separate model-defined input modes. CPU inference returns finite, L2-normalized 2,048-dimensional vectors. The pinned custom architecture was inspected before loading. The model cache and custom module cache stay in ignored `.cache/`. Loading the pinned local snapshot avoids an unrelated Transformers tokenizer metadata lookup and allows offline reuse. [Official model card](https://huggingface.co/voyageai/voyage-4-nano).

Chroma 1.5.9 through langchain-chroma 1.1.0 persists `policies_v1` under ignored `knowledge/index/chroma_v1`. Cosine distance is configured explicitly and telemetry is disabled. The build contains 28 whole heading sections; authored sections are bounded to 2,400 UTF-8 bytes. Larger sections fail for splitting rather than being silently truncated. Token-aware overlap splitting is unnecessary for this corpus and remains a documented extension. The manifest records model/revision/dimension/normalization, source hashes, chunking, rules and collection. Changed inputs require a new index version; incompatible or incomplete indices fail closed.

Policy search returns complete citation metadata, scores, threshold state and conflict details. It filters future and superseded sources and prefers policy authority for near-tied scores. Doc-type filtering is supported; category currently helps the explicit electronics conflict topic check rather than acting as a full category metadata filter. The declared R05 FAQ/policy conflict inserts both applicable sources deterministically; this is disclosed separately from vector retrieval quality. Overlapping retrieved versions are flagged, but broader conflicting-version corpus evaluation is future work.

## Measured retrieval

The 20 assistant-authored development labels were saved before evaluation: 15 answerable, 5 unanswerable. Threshold selection uses this same set, not an independent test set. The separately frozen ten-case holdout is not used for tuning.

| Measure | Result |
|---|---:|
| Candidate Recall@5 before threshold/conflict insertion | 100% |
| Candidate MRR | 0.90 |
| Calibrated cosine similarity threshold | 0.464133 |
| Recall@5 after threshold | 80% |
| Answerable queries fully rejected | 2/15 |
| Unanswerable queries rejected | 5/5 |
| R05 declared conflict | Detected, both sources retained |

The threshold favors abstention, reducing useful evidence coverage. L01 (TrailRunner paraphrase) and L15 (exception request) are rejected despite relevant raw candidates. Other relevant lower-ranked passages are also filtered. Candidate recall passes its 90% target, but post-threshold coverage does not; no claim of complete retrieval acceptance is made. Preserve these gaps for improvement and final evaluation rather than lowering the threshold silently.

[Retrieval summary](../artifacts/retrieval/summary.json) · [20-row CSV](../artifacts/retrieval/retrieval_eval.csv) · [three relevance examples](../artifacts/retrieval/relevance_examples.json) · [index manifest](../knowledge/index_manifest.json).

## RAG on/off experiment

Ten identical frozen policy cases were run in both modes with the same model/settings and a separately versioned Phase 4 prompt derived from C. This single-agent experiment has no order tools, writes, memory or verified escalation tickets; it does not claim the Phase 5 architecture is built.

| Mode | Validated outputs | Cited outputs | Policy success status | Escalation classification |
|---|---:|---:|---:|---:|
| No RAG | 9/10 | 0/10 | 0/10 | 0/10 |
| RAG | 10/10 | 9/10 | 7/10 | 1/10 |

R05 without evidence failed output grounding validation; the failure is preserved. With RAG, the model surfaced both sources and classified escalation. This is not proof of a ticket or the final RCA guard behavior. R01 remains insufficient evidence at the conservative threshold. Citation resolution and syntactic numeric screening pass for validated outputs; they do not establish semantic faithfulness or zero fabricated policy.

Evidence: [RAG run summary](../artifacts/rag_runs/20261013T203731Z/summary.json) and [all 20 outputs, including failures/repairs](../artifacts/rag_runs/20261013T203731Z/outputs.jsonl). [Same-model DeepEval faithfulness](../artifacts/rag_runs/20261013T203731Z/deepeval_faithfulness.json) measured nine context-bearing outputs: each scored 1.0. Eleven no-context outputs were skipped; no judge errors occurred. This is indicative self-evaluation, not independent validation; human calibration remains pending.

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
