"""CLI entrypoint.

Kept intentionally small: interaction layer validates and presents,
it owns no business rules (see docs/architecture.md, layer 1). Business logic for the
Phase 2 baseline lives in baseline_agent.py.
"""

from __future__ import annotations

import argparse
import sys
from datetime import date

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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="capstone-agent")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("status", help="show phase status").set_defaults(func=cmd_status)
    ask_p = sub.add_parser("ask", help="one-shot question against the Phase 2 rule baseline")
    ask_p.add_argument("message")
    ask_p.add_argument("--today", metavar="YYYY-MM-DD", help="pin the scenario clock for reproducible answers")
    ask_p.set_defaults(func=cmd_ask)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
