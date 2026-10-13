> Historical document. Superseded by [Architecture and Plan v3](../../architecture_and_plan.md). Not an active requirement.

# Phase 4 embedding recommendation

Candidate recommendation: **asymmetric retrieval with `voyage-4-large` document
embeddings and local `voyageai/voyage-4-nano` query embeddings, initially 1024
dimensions**. Compare with a nano-only baseline before selecting a default.
This is a proposed configuration, not an installed model or measured result.

The project has a small synthetic policy corpus and a frozen retrieval test set.
Local embeddings would allow reproducible indexing without a separate embedding API
key for the nano-only baseline. Asymmetric indexing requires Voyage API access for
`voyage-4-large`, while query embedding can run locally. Nano is open-weight under Apache 2.0, supports multilingual retrieval and
256/512/1024/2048 dimensions. When using Sentence Transformers, set 1024 explicitly
rather than relying on a default, and use `encode_query` / `encode_document` for
the correct retrieval prefixes. Pin the model revision and dependency versions.

Sources: [official model card](https://huggingface.co/voyageai/voyage-4-nano),
[Voyage embedding options](https://docs.voyageai.com/docs/embeddings).

Voyage states that the 4-series models share a compatible embedding space:
[Voyage 4 announcement](https://blog.voyageai.com/2026/01/15/voyage-4/).
Use the same output dimension, consistent normalization and precision, correct
query/document input types, and versioned index metadata. Embeddings from arbitrary
unrelated model families are not assumed compatible. Confirm the exact local model
revision, API document model ID, and observed vector dimensions before indexing.

The asymmetric design spends more effort on infrequent corpus embedding and less
on continuous query embedding. It is a promising production pattern; our small
capstone corpus still needs measured evidence that it improves retrieval enough to
justify the additional hosted dependency. No comparative quality is claimed yet.

Hosted comparison candidate: `voyage-4-lite`, positioned by Voyage for latency and
cost. This requires a separate Voyage credential and API integration. Neither the
local model nor hosted model has been downloaded/configured in this repository.

Evaluate both candidates on retrieval Recall@5, missing/conflicting-source cases,
latency and resource usage before claiming quality. Label relevant source sections
independently of the model output. Choose similarity thresholds from measured
answerable/unanswerable examples, not a universal assumed cutoff.

The answer-generation model stays separate: Qwen/OpenAI-compatible chat generates
responses, while the embedding model indexes documents and embeds search queries.
The first Phase 4 step is authoring the versioned synthetic policy corpus; embeddings
alone cannot resolve the current lack of authoritative evidence.
