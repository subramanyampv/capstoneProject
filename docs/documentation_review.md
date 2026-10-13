# Documentation review — 2026-10-12

## Current state

Phases 1 and 2 are recorded as complete. The repository contains the rule-based
baseline, synthetic structured records, a frozen evaluation dataset, unit tests,
and saved eight-request baseline evidence. Phase 3 (LLM integration and prompt
comparison) is the next planned step. Most architecture packages are placeholders;
the supervisor, specialists, retrieval, transaction controls, memory, and feedback
adaptation remain future work.

This review inspected Markdown documentation, source files, repository inventory,
and saved baseline evidence. It did not rerun tests or inspect the PDF contents.
Neither `.venv/` nor `../.venv/` exists. Per the user's mandatory environment rule,
Python execution must wait for an approved local virtual environment.

## Findings to resolve

1. **Safety claims exceed implementation.** README calls its invariants enforced,
   and architecture.md calls them tested behaviors. baseline_limitations.md correctly
   states that the baseline has no request-time safety gateway or confirmation flow.
   Distinguish target invariants from controls actually implemented and verified.
   Baseline log redaction currently covers SSNs and contiguous card-number patterns;
   it does not establish the broader credential/PII guarantees in the safety plan.
2. **Knowledge corpus is missing.** requirements.md calls seven policy documents
   frozen and present in `knowledge/raw/`, but that directory contains only
   `.gitkeep`. Create and version the corpus before grounded prompt comparisons
   and retrieval work; document any required change to the frozen requirements.
3. **Tool contract is incomplete.** requirements.md references eight tools in
   architecture.md, but that document does not enumerate eight tool contracts.
   Specify names, schemas, access categories, error behavior, and budgets before
   implementing orchestration.
4. **Evaluation status needs clarification.** evaluation_report.md says no
   implementation/evaluation results are claimed, while later text acknowledges
   Phase 2 evidence. Scope the disclaimer to the final-system evaluation.
   The baseline's 6/8 intent figure is a small scripted demonstration, not a
   measurement of the 65-case acceptance suite.
5. **Script inventory mixes existing and planned commands.** scripts/README.md
   lists five scripts; only run_baseline.sh exists. Label the remaining commands
   planned so a new contributor can identify runnable steps.
6. **Baseline runner permits global Python.** run_baseline.sh warns when no venv
   is active and then defaults to python3. Before future execution, require a local
   venv and fail if unavailable, consistent with the user's environment rule.
7. **Dependency reproducibility remains open.** pyproject.toml uses lower bounds
   without a lockfile, despite the engineering plan mentioning pinned dependencies.
   Choose a reproducible dependency workflow for Phase 3.

The README blueprint link was corrected to the PDF already tracked inside `docs/`
so it resolves from GitHub and standalone clones.

## Next session

- Resolve the virtual environment setup with the user before running Python.
- Reconcile implementation status, corpus claims, and the planned tool inventory.
- Select a model provider and model, establish configuration validation and a
  provider interface, and implement versioned prompts A/B/C with typed outputs.
- Capture actual prompt outputs on the frozen cases with controlled settings;
  distinguish unsupported future capabilities from Phase 3 failures.
- Preserve the existing baseline evidence and compare the known paraphrase and
  multi-intent failures without claiming future phases are already implemented.

## Continuation update

The user approved creation of the project `.venv` and chose a local OpenAI-compatible
server. The virtual environment, Phase 3 client/prompts/harness, documentation
clarifications, venv-only script guard and dependency constraints are now implemented.
See `prompt_evaluation.md` for current verification and remaining work. Live model
results are now preserved in `phase3_live_results.md`. The configured Qwen provider
completed 195 schema-valid responses; semantic defects still block default selection.
The embedding recommendation for Phase 4 is documented in `embedding_strategy.md`.
