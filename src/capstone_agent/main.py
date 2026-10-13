"""CLI entrypoint.

Kept intentionally small: interaction layer validates and presents,
it owns no business rules (see docs/architecture.md, layer 1). Business logic for the
Phase 2 baseline lives in baseline_agent.py.
"""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

PHASES = [
    (1, "problem framing & success definition — DONE"),
    (2, "rule-based Python baseline — DONE (single agent, deterministic rules)"),
    (3, "LLM integration & prompt evaluation"),
    (4, "knowledge & retrieval (RAG)"),
    (5, "tools & multi-agent orchestration"),
    (6, "planning, memory, context"),
    (7, "adaptive behavior"),
    (8, "deployment readiness"),
    (9, "evaluation & engineering review"),
]


def cmd_status(_: argparse.Namespace) -> int:
    print("capstone-agent — multi-agent e-commerce support agent")
    print("Phases:")
    for num, name in PHASES:
        active = num == 3
        print(f"  {'>' if active else ' '} phase {num}: {name}")
    print("\nTry:  capstone-agent ask \"Can I return order O-1001?\" --today 2026-10-12")
    print("Baseline evidence run:  scripts/run_baseline.sh")
    return 0


def cmd_ask(args: argparse.Namespace) -> int:
    from capstone_agent import baseline_agent  # lazy: status stays dependency-free

    today = date.fromisoformat(args.today) if args.today else None
    result = baseline_agent.respond(args.message, today=today)
    print(result.response)
    print(f"\n[intent={result.intent} matched={result.matched} latency={result.latency_ms}ms req={result.request_id}]")
    return 0


def cmd_llm_ask(args: argparse.Namespace) -> int:
    import json
    from capstone_agent.config import LLMConfig
    from capstone_agent.llm_agent import respond
    from capstone_agent.model_client import OpenAICompatibleClient

    config = LLMConfig.from_env(Path(args.env_file))
    result = respond(args.message, OpenAICompatibleClient(config), variant=args.prompt,
                     today=date.fromisoformat(args.today), secrets=(config.api_key,))
    print(json.dumps(result.as_dict(), indent=2))
    return 0 if result.outcome == "validated" else 1


def cmd_compare(args: argparse.Namespace) -> int:
    from capstone_agent.config import LLMConfig
    from capstone_agent.evaluation.prompt_comparison import ROOT, run_comparison
    from capstone_agent.model_client import OpenAICompatibleClient

    config = LLMConfig.from_env(Path(args.env_file))
    output = run_comparison(OpenAICompatibleClient(config), config,
                            dataset=ROOT / "data/evaluation_cases.json",
                            output_root=Path(args.output), today=date.fromisoformat(args.today),
                            case_ids=args.case, dry_run=args.dry_run, workers=args.workers,
                            client_factory=lambda: OpenAICompatibleClient(config),
                            progress=lambda case, prompt, outcome: print(f"{case} {prompt}: {outcome}", flush=True))
    print(f"Evidence: {output.resolve()}")
    if not args.dry_run:
        import json
        counts = json.loads((output / "summary.json").read_text())["counts"]
        if any(key.endswith(":error") and value for key, value in counts.items()):
            return 1
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="capstone-agent")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("status", help="show phase status").set_defaults(func=cmd_status)
    ask_p = sub.add_parser("ask", help="one-shot question against the Phase 2 rule baseline")
    ask_p.add_argument("message")
    ask_p.add_argument("--today", metavar="YYYY-MM-DD", help="pin the scenario clock for reproducible answers")
    ask_p.set_defaults(func=cmd_ask)
    llm = sub.add_parser("llm-ask", help="Phase 3 LLM-only request; no tools/actions")
    llm.add_argument("message")
    llm.add_argument("--prompt", choices=["A", "B", "C"], required=True,
                     help="explicit experimental variant; no default selected yet")
    llm.add_argument("--env-file", default=".env")
    llm.add_argument("--today", default="2026-10-12")
    llm.set_defaults(func=cmd_llm_ask)
    compare = sub.add_parser("compare-prompts", help="A/B/C comparison on frozen cases")
    compare.add_argument("--env-file", default=".env")
    compare.add_argument("--today", default="2026-10-12")
    compare.add_argument("--output", default="artifacts/prompt_runs")
    compare.add_argument("--case", action="append", help="optional subset; repeat for each case ID")
    compare.add_argument("--dry-run", action="store_true", help="save manifest without contacting model")
    compare.add_argument("--workers", type=int, default=1, help="1–4 independent concurrent model clients")
    compare.set_defaults(func=cmd_compare)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except ValueError as exc:
        # Configuration and input errors carry deliberately non-sensitive diagnostics.
        print(f"Configuration/input error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
