# Submission neutrality plan

This is a planning audit, not a release decision or an implemented export. Original source, experiment results, raw manifests and the existing independent AI review remain unchanged. No model identities are reproduced here. The public submission should describe configurable model roles and preserve honest evaluation provenance. Removing a name must never imply that results generalize to an untested replacement.

## Audit boundary and findings

Inspected tracked path inventory and selected source/documentation text. Excluded private environment configuration, sealed/blind/holdout contents, runtime logs, caches and application execution. Historical evidence paths were inventoried without reading their contents in this audit. This is a targeted model-reference inventory, not a complete secret or binary-content scan.

Concrete surfaces requiring review in a derived export:

| Current paths | Finding and proposed treatment |
|---|---|
| `README.md:41`, `README.md:43`, `README.md:47` | Configuration instructions expose provider/protocol and model-role details. Keep exact environment variable names and compatible protocol instructions; replace concrete configured identities with role aliases only in the derived narrative. |
| `docs/requirements.md:9`, `docs/retrieval_design.md:7`, `docs/engineering_justification.md:12`, `docs/problem_framing.md:13` | Current design prose contains concrete model choices. Publish a consolidated role-based architecture and document measured retrieval results as belonging to one pinned configuration. |
| `docs/architecture_and_plan.md`, `docs/project_progress.md`, `docs/task_list.md`, `docs/phase3_live_results.md`, `docs/prompt_comparison.md`, `docs/phase9_evaluation.md` | Long-form plans and experiment narratives mix identity details, development history and current claims. Derive a short current submission report; keep original narratives in the private research archive. |
| `docs/archive/v1-v2/`, `docs/archive/v3/` | Superseded documents and PDFs can reintroduce names and stale promises. Exclude from public package by allowlist; preserve untouched privately. |
| `knowledge/index_manifest.json:2` | Index metadata pins the actual embedding identity. Keep the original privately and retain exact pinning in runnable configuration; do not replace a machine-enforced identity with an alias unless an explicit mapping resolves to the exact same identity. |
| `src/capstone_agent/config.py:85`, `src/capstone_agent/main.py`, `src/capstone_agent/operations.py`, `streamlit_app.py:76` | Public settings, CLI status and UI can expose configured identity. A later export-only presentation projection should display role aliases; internal request configuration and index validation must retain real values. |
| `src/capstone_agent/retrieval/`, `src/capstone_agent/langchain_client.py`, `pyproject.toml`, `constraints-dev.txt` | Adapter filenames, imports and package dependencies contain provider/protocol-specific details. Do not mechanically rename dependencies, imports or protocol strings. Model-neutral presentation is compatible with honest implementation attribution. If a strict requirement forbids even provider names, document that runnable source needs a reviewed adapter refactor; a text substitution is unsafe. |
| `src/capstone_agent/evaluation/`, `scripts/run_final_suite.py`, `scripts/judge_final_suite.py`, `scripts/replay_final_style.py`, comparison scripts | Saved settings and judge manifests may contain configured identities. Only a derived publication view may alias them; raw locked manifests and score files stay byte-for-byte unchanged. |
| `artifacts/final_runs/`, `artifacts/prompt_runs/`, other dated experiment folders | Preserve original experiments privately. Publish only selected derived summaries and an explicitly selected review packet after privacy/identity inspection. No recursive artifact-folder inclusion. |
| `scripts/package_source.py` | Current script copies committed files with selected path exclusions and configured-key checks. It is not a neutrality exporter; it does not contain an explicit unused-blind exclusion. Do not run it as the final public-package solution without an allowlist and dedicated blind exclusion. |

The line numbers above describe the audit snapshot and may shift with concurrent work. No private configured identities were read.

## Proposed curated layout

Create a separate `submission/public/` staging directory only after source and acceptance gates are resolved. This audit creates no such package or ZIP.

```text
submission/public/
  README.md
  SETUP.md
  LIMITATIONS.md
  SOURCE_PROVENANCE.json
  docs/
    architecture.md
    evaluation.md
    safety_and_privacy.md
    demo_script.md
    neutrality_disclosure.md
  source/
    src/
    tests/
    config/
    knowledge/raw/
    data/                         # explicit synthetic fixtures/public used cases only
    scripts/                      # explicit runnable allowlist
    pyproject.toml
    requirements.txt
    constraints-dev.txt
    .env.example                  # placeholder configuration only
  evidence/
    current_candidate/
      run_summary.json
      safety_repeats_summary.json
      quality_scores_summary.json
      review_summary.json
      limitations.json
    experiments/
      prompt_comparison_summary.json
      retrieval_comparison_summary.json
      capability_comparison_summary.json
  MANIFEST.json
```

`source/` is runnable implementation evidence. Dependency and protocol attribution remains accurate; generic aliases are for display and derived reports. `SETUP.md` must require an existing approved local venv and use its binaries, explain credential placeholders, and state that using another model requires fresh validation. Include fixture files from `data/` by explicit filenames such as `sample_orders.json`, `sample_tracking_events.json`, `policy_rules.json`, and `evaluation_cases.json` only after verifying they contain authorized synthetic/public data. Include a frozen context file only if it belongs to the public frozen suite. Never infer publication permission from Git tracking alone.

Place the untouched original checkout/evidence in a private research archive outside the staged public tree. Do not move, delete, rewrite, relabel or clean the originals. Preserve original manifests, failed/interrupted runs, previous scores, report provenance and their hashes. An ignored local alias map may live outside the public tree, but contains only role-to-configuration references, never credentials. A public disclosure should say that detailed provider identifiers were omitted from presentation while original locked configuration remains available to the owner. If the rubric demands exact model disclosure, resolve that requirement explicitly; do not silently claim full reproducibility without identity information.

## Generic public aliases and provenance

| Role | Public alias |
|---|---|
| Primary answer generation and tool planning | `Application Model A` |
| Primary quality judge sharing application identity | `Judge A (same model as Application Model A)` |
| Genuinely different configured judge, only when verified | `Judge B (separate model)` |
| Pinned document/query embedding configuration | `Embedding Model E1` |
| Alternate embedding backend evaluated separately | `Embedding Model E2` |
| Development prompt variants | `Prompt A`, `Prompt B`, `Prompt C` |
| Independent answer-packet AI reviewer | `Independent AI Proxy Reviewer` |

Aliases must be stable by underlying identity/configuration, not merely by filename. Do not call a differently prompted or independently invoked copy of the same model an independent model. Preserve the distinction between same-model automated judging, separate-model judging, an independent-context AI proxy review, and actual human calibration. The existing twenty-case independent review is AI-authored; its original JSON and companion notes must remain unchanged. If its public copy is transformed, name it a derived summary, retain the original packet/review hashes privately, and give it its own hash rather than pretending transformed bytes match the original.

A later export should produce an allowlist manifest with source commit plus dirty-tree digest, original-to-derived path mapping, alias schema version, transformation description, and SHA-256 for every exported file. Document any excluded reproducibility metadata. Never publish a bare hash of a secret. Alias conversion must not modify questions, expected outcomes, policy values, scope, scores, errors, unsafe-claim flags or case identifiers. No acceptance result can be inherited across an application-source change solely because names were removed.

## Remaining blockers and rubric risks

1. **Current-build evidence alignment:** `docs/current_status.md` identifies an uncommitted remediation candidate and a current judging run, while `docs/evaluation_report.md` still contains older candidate narratives. A public report must name exactly one build/run chain and clearly separate historical results. Concurrent work may supersede the ledger read here; reconcile at export time.
2. **Readiness is unproven by this audit:** complete current-build frozen evaluation, fixed-rubric quality scoring, independent review, safety repeats, actual ticket read-back, privacy checks and required memory/UI/tracing evidence. This planning audit establishes none of those gates. Record failed/unavailable metrics and correctness separately from latency.
3. **Human-calibration claims:** the evaluation report has an AI-authorship caveat but retains body claims of actual human review. Derived public prose must resolve provenance consistently. AI proxy ratings cannot satisfy a rubric that requires actual human calibration unless the assessor explicitly permits the substitution.
4. **Blind-data separation:** unused sealed/blind files remain unopened and local. Any one-shot blind evaluation must follow its current authorization and locking policy; publish used cases only after first evaluation with results. Never sweep all tracked evaluation files into a package.
5. **Original-scope gaps:** transaction execution and pending-action confirmation flows remain deferred. Describe eligibility information and verified local mock handoffs accurately; do not count excluded legacy action criteria as passed. Production account ownership and real retailer integration are not established by synthetic fixtures.
6. **Protected deliverables:** retain five required demos, failure evidence, reset and adaptation before/after, root-cause before/after, capability comparisons, and clear setup instructions. A concise neutral package must not omit rubric evidence simply to hide experiment details.
7. **Reproducibility versus identity omission:** exact embedding pinning is machine-enforced, and results are configuration-specific. Provider-agnostic setup alone does not prove equivalent quality with another configuration. State this limit and preserve exact private configuration provenance.
8. **Packaging boundaries:** no private environment files, Git history, runtime stores, raw logs, caches, unused blind inputs, local alias map, stale PDFs or abandoned intermediate reports. Check links in staged documents, inspect selected images/PDFs and archive inventory, and test the curated source in an approved existing venv without creating one silently.
9. **Snapshot timing:** `scripts/package_source.py` exports committed bytes, so uncommitted fixes would be absent. Resolve the intended source snapshot before packaging and verify every exported file hash. A previous historical credential issue is documented in README; retain a history-free package and scan the selected bytes without exposing configured values.

No source edits, external requests, packaging, publication, blind-data access or release acceptance were performed by this audit. Only this planning document was written.
