# Retrieval Proof

These are preserved development-stage measurements, not final-runtime acceptance or causal proof about the completed support graph. The [derived evidence](../evidence/retrieval_comparison.json) includes every recorded paired answer, selected follow-up, calibration row and source-file SHA-256. This link targets the final staged package. Synthetic order identifiers are minimized with the existing exporter; answer claims, statuses and failures are retained. Original deployment identities remain private; public roles are `application_model`, `same_application_model_self_judge` and `retrieval_embedding_model`. The evidence was derived without new model requests or changes to originals.

## Corpus and index design

The historical v2 calibration index contains seven synthetic policy/FAQ documents and 28 complete authored heading sections. Each section is bounded to 2,400 UTF-8 bytes; oversized sections require explicit splitting rather than truncation. No overlap is used for these short authored sections. Embeddings are finite, normalized, 2,048-dimensional vectors; the persistent vector collection uses cosine distance. Model identity, document hashes, chunking and metadata profile determine index compatibility. The public proof omits the private model identifier and revision.

Retrieved sections carry document, section, version, authority and effective-date metadata. Category-applicability fields scope specific sections while general rules remain available to all relevant categories. Future/superseded evidence is excluded. Category and document filters are supported, with declared conflict handling retaining both applicable sources even when this exceeds requested `k`. An inserted source with no vector score has `null`, not a fabricated similarity.

The paired answer experiment below used **index v1**; the separately recorded retrieval calibration used **index v2**. They must not be represented as one experiment.

## Retrieval calibration and relevance

Twenty assistant-authored development labels comprise fifteen answerable queries and five unanswerable queries. Threshold **0.464133** was selected on this same set to maximize balanced answerability accuracy. This is calibration, not held-out validation.

| Measure | Recorded result | Denominator and interpretation |
|---|---:|---|
| Raw candidate Recall@5 | 1.00 | Mean over 15 answerable queries |
| Raw candidate reciprocal-rank mean | 0.90 | 15 answerable queries |
| Recall@5 after threshold | 1.00 | Mean over 15 answerable queries |
| Answerable queries fully rejected | 0/15 | No complete abstention on this development set |
| Correct unanswerable abstention | 5/5 | Five authored negatives; not general out-of-domain accuracy |

For the paraphrased shoe-return query, the footwear FAQ ranks first at **0.611955**, but is not the labeled governing section. The actual return-window section ranks second at **0.519976** and is labeled relevant. Similarity alone therefore does not establish policy authority. For the weather query, the top score is **0.302195**; all three illustrated sections are irrelevant and the search abstains.

The electronics conflict example has two labeled relevant sources. The dedicated `k=1` category diagnostic retains both conflicting references and explicitly reports that evidence exceeds `k`. This is deterministic declared-conflict handling, excluded from raw vector-retrieval quality claims. Broad category probes still abstain for footwear, apparel, home and perishables at the calibrated threshold; the narrower perishable-exclusion probe retrieves its exclusion section. Those preserved abstentions prevent a misleading universal category-success claim.

## Paired retrieval-off/on answers

Ten identical public policy cases ran in both modes: **20 total outputs**, same recorded application model/settings, temperature 0, 1,200 completion-token cap, and the same historical single-agent prompt. There were no order tools, memory, transaction writes or verified escalation tickets.

| Recorded outcome | Retrieval off | Retrieval on |
|---|---:|---:|
| Schema/grounding-validated outputs | 10/10 | 10/10 |
| Outputs with citations | 0/10 | 10/10 |
| Policy-success status | 0/10 | 8/10 |
| Escalation classification | 0/10 | 1/10 |
| Recorded validation errors | 0/10 | 0/10 |

Validation here checks citation resolution and syntactic numeric grounding. These counts do not establish semantic accuracy. Success and escalation are model classifications, not confirmed customer resolutions or human handoffs.

R01 without retrieval says it cannot confirm return eligibility because policy evidence is absent. With retrieval, it supplies the cited 30-day footwear rule, while disclosing that the specific order is unverified. R05 without retrieval cannot choose between alleged windows; with retrieval it surfaces the conflicting 30-day FAQ and 15-day policy and classifies escalation. Its historical statement “I am escalating” is not proof of ticket creation: this experiment had no ticket tool.

## Preserved semantic failure and selected repair

R02 with retrieval incorrectly said a refund deadline “kicks in after 30 days.” The source defines an inclusive return window, not an independent refund deadline. Same-model faithfulness scored this output **0.6667**, below the **0.90** threshold. Nine other retrieval-enabled answers scored 1.0. Ten empty-context answers were skipped, not passed. These are indicative self-judge results without actual-human calibration.

A revised prompt was tested only on **R01, R02, R05 and R08** in both modes: eight outputs. Both modes validated 4/4; retrieval-on cited 4/4, with two success classifications and one escalation classification. Four context-bearing answers scored 1.0; four no-context answers were skipped. R02 now explicitly separates the return window from a refund deadline or processing time. The original failure remains in the derived evidence.

This selected four-case follow-up does **not** replace a complete revised-prompt ten-case rerun. These records also do not contain a current-final-runtime retrieval-off/on experiment. The full current-build [Evaluation Report](Evaluation_Report.md) must report those gaps separately and cannot use the historical stage results to waive final safety or semantic-review requirements.
