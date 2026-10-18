# Release human calibration — actual supplied ratings

Twenty human-reviewed cases, 56 paired applicable ratings, 82.14% threshold agreement; mean absolute difference 0.0719. No human-flagged unsafe/fabricated claims. Four faithfulness ratings are explicitly inapplicable without retrieval context. Earlier baseline ratings are preserved separately.

Ten threshold disagreements remain: nine answer-relevancy cases (N01, N03, N07, R09, R14, S04, M02, M05, M11) and S07 grounded support. Human scores pass these thresholds; the same-model judge scores do not. The judge often penalizes supporting JSON/reasons or generic refusal wording. That is an interpretation of observed reasons, not proof the human or judge is universally correct. Scores and rubric are unchanged.

Human means: faithfulness 1.0 across 16 applicable cases, relevancy .985 across 20, grounded support 1.0 across 20. Selection is the predetermined twenty-case sample; no claim of all-case human grading. The missing M09 faithfulness judgment in the all-65 run remains unavailable; it is outside the calibration sample.

The completed review, unchanged application/model and exact judged-output SHA were checked before holdout questions were first inspected. Ten identity/setup/outcome contexts were then fixed and committed as 6e4346a before any holdout answers. There is no application/prompt tuning after inspection.
