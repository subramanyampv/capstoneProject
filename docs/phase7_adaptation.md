# Phase 7 — controlled response style adaptation

Implemented 2026-10-16 under architecture revision 3.1. The terminal and Streamlit call the same `run_support` entry point and `PreferenceStore`; neither interface owns adaptation or business rules.

## Commands and controls

Start terminal chat with `.venv/bin/capstone-agent support --chat --customer C-100`. One-shot commands work too, for example `.venv/bin/capstone-agent support '/feedback too_long' --customer C-100`.

| Command | Effect |
|---|---|
| `/feedback enable` | Consent to automatic style learning for the selected synthetic customer |
| `/feedback disable` | Stop learning and use defaults; retain saved preferences until deletion |
| `/feedback too_long` / `too_short` | Record a length signal; submitting explicit feedback also enables learning |
| `/feedback unclear` | Record a request for numbered explanations |
| `/feedback helpful` / `not_helpful` | Record satisfaction only; no automatic style change |
| `/feedback reset_style` | Versioned rollback to standard prose; clear pending signals |
| `/forget-preferences` | Delete that customer's profile, history and feedback; learning returns to off |
| `/reset` | Delete session context; saved style preferences remain |

Streamlit's Support agent mode exposes the same settings and five feedback buttons. Feedback buttons appear after an answer for the current synthetic account, and disappear on account/session changes. The last rendered answer survives feedback reruns. No model or embedding/index initialization is needed for commands. The account selector is a demo identity boundary, not production authentication.

## Adaptation and authority

Only `verbosity` (concise, standard, detailed) and `format` (prose, bullets, step_by_step) enter a validated immutable style object. Two unused matching direction signals among the last ten move one length step or choose numbered steps. Consumed pairs cannot move another step on every subsequent request. At bounds, signals are consumed without creating a fictitious change. Consent changes record a UTC timestamp. Every actual change increments the version and records from/to, reason, signals and UTC timestamp. Reset creates a new version even at defaults.

Implicit learning requires consent and a prior successfully answered turn. Brevity/detail phrases become allowlisted signals. Repeated questions compare transient masked user text from the previous two turns using the existing pinned local Voyage-nano query embeddings, with cosine threshold **0.98**. Explicit order/SKU identifiers must match. That threshold is a conservative development default, not calibrated semantic performance. No embedding or raw message is saved in the preference store. Embedding failure skips repetition learning. Disabling session memory disables implicit history-based learning; explicit commands still work.

Original input is checked against the same deterministic refusal/escalation rules before implicit learning. Safety requests cannot supply implicit style signals. The composer receives generated presentation instructions only; the planner, specialist prompts, tool registry, eligibility logic, evidence gates and escalation rules never receive customer-editable configuration. Concise targets 80 answer words and bullets; detailed targets 250 words. Safety disclosures and complete evidence take priority. Responses are never blindly truncated. Measured word counts cover the main `answer`, excluding separately rendered reasons, sources and next steps.

## Persistence, privacy and deletion

Ignored `data/runtime/prefs.json` is authoritative, keyed by an opaque customer hash. Profiles persist across terminal processes and Streamlit sessions until deletion. Consent is off initially; explicit feedback grants it with disclosure in both interfaces. Each profile retains ten signal categories and twenty version changes. `feedback.jsonl` is a derived reporting view with only UTC timestamp, opaque customer reference, generated request reference, category and explicit/implicit type. It contains no free text, customer IDs, prompts, vectors or tool payloads. Reporting retention is 30 days and at most 10,000 events globally, pruned on access. Preference history remains until deletion, with the stated count bound.

A thread lock plus a local process file lock serialize read-modify-write. Files use owner-only permissions and atomic replacement. Both authoritative data and the derived log are updated before a successful command returns. A crash between replacements can leave a stale reporting view; the next successful access rebuilds it from authoritative data. There is no distributed lock, encryption at rest, forensic disk erasure or production account management. `/forget-preferences` removes the customer's retained feedback as well as profile/history; other customers remain intact. Operational request logs retain only command outcomes/style metadata, without feedback bodies.

Support requests fall back to default style if preference storage cannot be read. Commands report failure rather than falsely confirming deletion. The optional preferences store can be injected for isolated development experiments so the user's demo preferences are untouched.

## Verification

Offline tests cover thresholds, consumed pairs, customer isolation, persistence, concurrent updates, bounded history, helpfulness-only logging, opt-in/out, versioned reset, full scoped deletion, duplicate feedback references, closed style inputs, implicit signals, embedding failure, provider-independent commands, terminal chat and Streamlit account/feedback controls. Scripted graph tests exercise refusals and injury escalation across standard, concise and detailed styles, and verify style instructions reach only composition.

Run `make compare-style` for live synthetic before/after/reset and four safety cases in standard versus concise style. Evidence is recorded under `artifacts/style_runs/`; source snapshots, sanitized responses, word counts, versions, safety outcomes and deletion checks are preserved. Run `.venv/bin/python scripts/probe_style_repetition.py` for the conservative exact-repeat/paraphrase/different-product development probe. Run `make scan-style` for configured-key and known-canary scanning. The current evidence report is [Phase 7 validation](../artifacts/phase7_validation.md).

This is bounded per-customer presentation adaptation. It does not prove semantic faithfulness, optimize global customer satisfaction, change safety policy, or replace the Phase 9 frozen/holdout and human calibration gates. Implicit requests can be ambiguous and repetition is only a heuristic. Small samples can overreact; users can disable, reset or delete learned preferences.
