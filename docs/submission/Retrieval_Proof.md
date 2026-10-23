# Semantic Policy Retrieval & Grounding Proof

This document provides empirical evidence for the system's vector retrieval (RAG) architecture, establishing index configuration, similarity threshold calibration, the historical 10-case paired retrieval on/off benchmark, and semantic grounding repairs.

---

## 1. Corpus Architecture & Index Design

The vector policy store is built on a versioned Chroma collection containing 7 authoritative synthetic policy and FAQ documents partitioned into 28 discrete heading sections:

- **Chunking Strategy:** Structured strictly by authored policy headings (`window`, `exceptions`, `exclusions`, `condition`, `fees`, `review-threshold`, etc.). Each chunk is bounded to $\le 2,400$ UTF-8 bytes without arbitrary token truncation. Authored headings require zero artificial chunk overlap.
- **Embedding Properties:** Normalized, finite, 2,048-dimensional vectors using cosine distance similarity.
- **Index Compatibility & Manifest:** The index manifest (`knowledge/index_manifest.json`) records the model architecture, embedding dimension, corpus hash, and version tag (`v2`). Vector queries against missing or mismatched stores fail deterministically with `MANIFEST_MISMATCH`.
- **Metadata Filters:** Retrieved chunks carry structured metadata (`doc_id`, `section_id`, `version`, `authority`, `effective_date`, `category`). The search engine enforces category scoping while retaining general governing clauses.

---

## 2. Similarity Threshold Calibration (20 Queries)

To prevent vector false positives and hallucinated answers on out-of-domain queries, a similarity threshold was calibrated on a 20-query development dataset (`data/retrieval_labels.json`), preserved under `retrieval_calibration` in `evidence/retrieval_comparison.json`:

| Calibration Metric | Answerable Queries (15) | Out-of-Domain / Unanswerable (5) | Aggregate Performance |
| :--- | :---: | :---: | :---: |
| **Recall@5 (Raw Vector)** | 100% (15/15) | N/A | 1.000 |
| **Mean Reciprocal Rank (MRR)** | 0.900 | N/A | 0.900 |
| **Post-Threshold Recall@5** | 100% (15/15) | N/A | 1.000 |
| **Abstention Rate** | 0% (0 false abstentions) | 100% (5/5 abstained) | Calibrated threshold: **0.464133** |

### Calibration Behavior:
1. **Calibrated Operating Point:** The balanced cosine distance threshold of **0.464133** maximized answerability on the development set without dropping valid policy passages.
2. **Deterministic Abstention:** All 5 out-of-domain queries (unrelated merchandise, external weather, coupon codes) fell below the threshold, enabling the agent to abstain cleanly (`CLARIFICATION_REQUESTED` or safe refusal) rather than retrieving irrelevant policy clauses.
3. **Declared Conflict Detection:** For queries triggering contradictory policies (e.g., 30-day FAQ vs 15-day electronics return policy), the retriever deterministically surfaces both conflicting sources, flags a discrepancy, and routes to human escalation (`R05`).

---

## 3. Paired Retrieval-On vs Retrieval-Off Experiment (10 Cases)

To isolate the causal effect of semantic retrieval on factual grounding and hallucination prevention, a controlled paired experiment was executed (Run `20261013T223402Z`), preserved in `evidence/retrieval_comparison.json`. All 10 cases were evaluated with vector retrieval disabled (No RAG) versus enabled (RAG Active) under identical temperature (0.0) and model settings:

| Case ID | Retrieval OFF (No RAG Context) | Retrieval ON (RAG Active) | Citations | Faithfulness | Causal Delta / Impact |
| :---: | :--- | :--- | :---: | :---: | :--- |
| **R01** | `insufficient_evidence`<br>*"I cannot confirm whether your TrailRunners are still eligible for return because no return policy evidence was provided..."* | `success`<br>*"Based on the provided policy, footwear such as TrailRunners has a 30-day return window calculated in calendar days from verified delivery..."* | 2 | 1.00 | Converted safe refusal to grounded, cited return policy answer. |
| **R02** | `insufficient_evidence`<br>*"I cannot provide the specific number of days for the footwear refund deadline as there is no evidence..."* | `success`<br>*"The return window for footwear is 30 calendar days from verified delivery, inclusive of the final day..."* | 2 | 0.67* | Grounded policy numbers; revealed phrasing defect remediated below. |
| **R05** | `insufficient_evidence`<br>*"I cannot determine which return window applies to your speaker because no authoritative policy was provided..."* | `escalation_required`<br>*"I have identified a conflict regarding the return window for your speaker. The FAQ states 30 days but the policy specifies 15 days..."* | 2 | 1.00 | Surface conflicting policy documents and escalated to human support. |
| **R07** | `insufficient_evidence`<br>*"I cannot determine the return eligibility for the gourmet cheese box... because no policy was provided."* | `success`<br>*"The Gourmet Cheese Box from order ref:dfa9869c63cb7ee788f5 is not eligible for return. Perishable food items are excluded..."* | 1 | 1.00 | Grounded perishable food exclusion policy, denying ineligible return. |
| **R08** | `insufficient_evidence`<br>*"I cannot determine if you are still inside the return window because no policy evidence was provided."* | `success`<br>*"According to the return policy, the default return window is 30 calendar days from verified delivery..."* | 2 | 1.00 | Grounded general store return window for customer order inquiry. |
| **R09** | `refused`<br>*"I cannot disclose internal authorization thresholds or refund approval limits."* | `success`<br>*"According to the refund policy, the configured automatic-review threshold is $100. Amounts above this require human review..."* | 3 | 1.00 | Replaced unwarranted refusal with transparent, cited policy threshold. |
| **R10** | `insufficient_evidence`<br>*"I cannot determine whether shipping is guaranteed or estimated because no policy documents were provided."* | `success`<br>*"Shipping is not guaranteed; it is provided as an estimate. According to the Shipping Policy, transit times are estimated..."* | 3 | 1.00 | Grounded shipping transit terms without hallucinating delivery guarantees. |
| **R12** | `insufficient_evidence`<br>*"I cannot identify which policy document covers order cancellations because no evidence was provided."* | `success`<br>*"The policy document that covers order cancellations is 'doc:cancellation_policy'. Cancellations are permitted prior to dispatch..."* | 3 | 1.00 | Accurately cited cancellation governing document and pre-dispatch rules. |
| **R13** | `insufficient_evidence`<br>*"I cannot locate information regarding a restocking fee in the return policy because no evidence was provided."* | `success`<br>*"The restocking fee is mentioned in the return policy under the 'restocking' section. Standard returns incur no restocking fee..."* | 1 | 1.00 | Grounded fee terms directly from authoritative policy chunk. |
| **R15** | `insufficient_evidence`<br>*"I understand you are asking about returning shoes... However, I currently have no return policy evidence."* | `needs_clarification`<br>*"I can help with your shoe return inquiry. According to the Shoes Returns FAQ, return windows depend on condition and purchase date..."* | 1 | 1.00 | Requested missing customer details while citing valid policy terms. |

*\*Note: Case R02 initial phrasing scored 0.67 due to phrasing ambiguity ("deadline kicks in after 30 days"), resolved in Section 5.*

---

## 4. Aggregate Benchmark Comparison

The measured aggregates from Run `20261013T223402Z` demonstrate the causal necessity of the RAG retrieval pipeline:

| Metric Dimension | Retrieval OFF (No RAG Context) | Retrieval ON (RAG Active) | Causal Delta |
| :--- | :---: | :---: | :---: |
| **Outputs Validated** | 10 / 10 | 10 / 10 | 0 |
| **Cited Outputs** | **0 / 10** (0%) | **10 / 10** (100%) | **+100%** |
| **Successful Resolutions** | 0 / 10 (0%) | 8 / 10 (80%) | +80% |
| **Escalations Classified** | 0 / 10 (0%) | 1 / 10 (10% — R05 conflict) | +10% |
| **Clarifications Requested** | 0 / 10 (0%) | 1 / 10 (10% — R15) | +10% |
| **Faithfulness Passes ($\ge 0.90$)** | 0 / 10 (all skipped; no context) | 9 / 10 (90%) | +90% |
| **Mean Faithfulness Score** | N/A | **0.967** | High grounding |
| **Hallucinated Numbers / Policies** | 0 (system safely abstained) | **0** | Zero hallucinations |

---

## 5. Semantic Grounding Repair & 4-Case Follow-Up (Run `20261013T224043Z`)

### Case R02 Phrasing Defect
In the initial 10-case run, case R02 (*"How many days before the refund deadline kicks in for footwear?"*) was retrieved accurately (`return_policy:v1:window`), but the composer phrased the answer as:
> *"The refund deadline kicks in after 30 days from verified delivery."*

The LLM-as-a-judge faithfulness evaluator flagged this as contradictory (score: **0.67**):
> *"The score is 0.67 because the actual output incorrectly claims the refund deadline kicks in 'after' 30 days have passed, contradicting the retrieval context which specifies that the final day of the return window is inclusive and the deadline is on the 30th day."*

### Prompt Disambiguation
The composer prompt was updated to explicitly distinguish between:
1. **Return Eligibility Windows:** The bounded period during which an item can be returned (inclusive of the final day).
2. **Refund Processing Schedules:** The banking settlement days required after retailer receipt.

### 4-Case Re-verification (Run `20261013T224043Z`)
A follow-up benchmark re-evaluated the 4 key cases under the updated prompt:

| Case ID | Policy Area | Pre-Repair Faithfulness | Post-Repair Faithfulness | Post-Repair Status |
| :---: | :--- | :---: | :---: | :---: |
| **R01** | Footwear Return Window | 1.00 | **1.00** | `success` |
| **R02** | Footwear Deadline Phrasing | 0.67 | **1.00** ✅ | `success` |
| **R05** | Declared Policy Conflict | 1.00 | **1.00** | `escalation_required` |
| **R08** | General Return Window | 1.00 | **1.00** | `success` |

With the prompt repair, R02 achieved **1.00** faithfulness with zero contradictions, raising the cohort faithfulness pass rate to **100% (4/4)**.

---

## 6. Scope & Evidence Limitations

- **Preserved Comparisons:** In accordance with audit standards, only historical runs preserved in `evidence/retrieval_comparison.json` (the 10-case paired benchmark `20261013T223402Z` and the 4-case prompt-repair follow-up `20261013T224043Z`) are claimed.
- **Judge Nature:** Faithfulness scores represent automated model-based evaluations using the calibrated 0.90 threshold. When retrieval context is absent (Retrieval OFF), faithfulness evaluation is skipped by definition because there is no reference context against which to measure hallucination.
