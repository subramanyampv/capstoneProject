> Historical document. Superseded by [Architecture and Plan v3](../../architecture_and_plan.md). Not an active requirement.

# Forced Demo Script (five interactions)

Use fixed synthetic records; capture actual execution traces. Designed to make
required capabilities visible to an evaluator. **Status: script only — no runs yet.**

## Demo 1 — Grounded return eligibility
Input: "I received my shoes 12 days ago. Can I return them?"
Expected: retrieve footwear policy, verify delivery date if needed, calculate
eligibility deterministically, cite source, offer simulated action only if permitted.
Capture: retrieved chunks, policy result, citation, final answer.

## Demo 2 — Multi-agent coordination
Input: "My package is delayed, and I want to know whether I can request a refund."
Expected: Logistics retrieves shipment events; Returns/policy service evaluates the
policy question; orchestrator merges validated results; clarify/escalate if evidence missing.
Capture: routing trace, specialist results, evidence, final decision.

## Demo 3 — Safety and transaction gate
Input: "Cancel my order immediately."
Expected: verify order + dispatch state, check cancellation policy, show exact action
summary, require matching confirmation, execute simulated action, verify result.
Capture: pending state, confirmation, action event, final state.

## Demo 4 — Missing evidence and escalation
Input: "I want a refund outside the return window, and the product caused an injury."
Expected: recognize safety complaint + policy exception; do not auto-approve; create
sanitized human handoff; verify ticket creation.
Capture: safety classification, policy decision, escalation reason, handoff result.

## Demo 5 — Feedback and memory
Sequence: ask a product/shipping question -> submit "too verbose" feedback -> repeat
question -> follow-up -> reset session -> repeat follow-up.
Expected: approved style adjustment, before/after output, working short-term context,
reset removes prior context.
Capture: feedback event, configuration version, outputs, reset test.

## Additional forced negative test
Invoke a nonexistent tool or inject a controlled timeout. Show the error trace and
prove no unauthorized action executed.

## Evidence checklist (every demo)
- Test case ID, input, application version, prompt version, knowledge-index version.
- Sanitized orchestration trace + retrieved source references.
- Tool inputs/outputs with sensitive fields removed.
- Final response, expected result, pass/fail, evaluator notes.
- Screenshots for presentation; logs/test outputs are the primary correctness evidence.
