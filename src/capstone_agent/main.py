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
    (3, "LLM integration & prompt evaluation — DONE (v3 selects Prompt C; final safety open)"),
    (4, "knowledge & retrieval (RAG) — DONE (development scope; final holdout open)"),
    (5, "tools & multi-agent orchestration — DONE (core; final acceptance open)"),
    (6, "planning, memory, context — DONE (bounded session scope; final evaluation open)"),
    (7, "adaptive behavior — DONE (bounded style; final evaluation open)"),
    (8, "deployment readiness — DONE (local deployment and hosted metadata observability)"),
    (9, "evaluation & engineering review"),
]


def cmd_evaluate_support(args):
    import json
    from capstone_agent.evaluation.support_runner import run_evaluation
    contexts=json.loads(Path(args.contexts).read_text()) if args.contexts else None
    result=run_evaluation(args.dataset,args.output,contexts=contexts,allow_holdout=args.allow_holdout,
        repeats=args.repeats,dry_run=args.dry_run)
    print(json.dumps(result,indent=2));return 0


def cmd_doctor(args):
    import json
    from capstone_agent.operations import doctor
    report=doctor(index=args.index)
    print(json.dumps(report,indent=2));return 0 if report['passed'] else 2


def cmd_status(_: argparse.Namespace) -> int:
    print("capstone-agent — multi-agent e-commerce support agent")
    print("Phases:")
    for num, name in PHASES:
        active = num == 9
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
    from capstone_agent.langchain_client import LangChainChatClient
    from capstone_agent.observability.langsmith_tracing import ObservabilityConfig

    config = LLMConfig.from_env(Path(args.env_file))
    obs = ObservabilityConfig.from_env(Path(args.env_file))
    with LangChainChatClient(config) as client:
        result = respond(args.message, client, variant=args.prompt,
                         today=date.fromisoformat(args.today), secrets=(config.api_key, obs.api_key), observability=obs)
    print(json.dumps(result.as_dict(), indent=2))
    return 0 if result.outcome == "validated" else 1


def cmd_compare(args: argparse.Namespace) -> int:
    from capstone_agent.config import LLMConfig
    from capstone_agent.evaluation.prompt_comparison import ROOT, run_comparison
    from capstone_agent.langchain_client import LangChainChatClient
    from capstone_agent.observability.langsmith_tracing import ObservabilityConfig

    config = LLMConfig.from_env(Path(args.env_file))
    obs = ObservabilityConfig.from_env(Path(args.env_file))
    output = run_comparison(LangChainChatClient(config), config,
                            dataset=ROOT / "data/evaluation_cases.json",
                            output_root=Path(args.output), today=date.fromisoformat(args.today),
                            case_ids=args.case, dry_run=args.dry_run, workers=args.workers,
                            client_factory=lambda: LangChainChatClient(config), observability=obs,
                            progress=lambda case, prompt, outcome: print(f"{case} {prompt}: {outcome}", flush=True))
    print(f"Evidence: {output.resolve()}")
    if not args.dry_run:
        import json
        counts = json.loads((output / "summary.json").read_text())["counts"]
        if any(key.endswith(":error") and value for key, value in counts.items()):
            return 1
    return 0


def cmd_evaluate(args):
    from capstone_agent.evaluation.deepeval_runner import evaluate_saved_outputs, ConfiguredJudge
    from capstone_agent.evaluation.prompt_comparison import ROOT
    from capstone_agent.config import LLMConfig
    judge = ConfiguredJudge(LLMConfig.from_env(Path(args.judge_env_file))) if args.judge_env_file else None
    report = evaluate_saved_outputs(Path(args.run_dir), ROOT / "data/evaluation_cases.json",
                                    judge=judge, case_ids=args.case)
    failed = sum(metric["pass"] is False for row in report["results"] for metric in row["metrics"])
    incomplete = sum(bool(metric.get("error_category")) for row in report["results"] for metric in row["metrics"])
    print(f"DeepEval: {len(report['results'])} outputs evaluated; {failed} metric failures.")
    if incomplete:
        print(f"{incomplete} judge scores unavailable; quality not measured.")
    print(f"Evidence: {Path(args.run_dir).resolve() / 'deepeval_results.json'}")
    return 1 if failed or incomplete else 0


def cmd_ingest(args):
    import json
    from capstone_agent.retrieval.configured_embeddings import ConfiguredEmbeddings
    from capstone_agent.retrieval.chroma_store import ingest
    manifest = ingest(ConfiguredEmbeddings(), version=args.index_version)
    print(json.dumps(manifest, indent=2))
    return 0


def cmd_search_policy(args):
    import json
    from capstone_agent.retrieval.configured_embeddings import ConfiguredEmbeddings
    from capstone_agent.retrieval.chroma_store import PolicySearch
    from capstone_agent.safety.redaction import sanitize_data
    result = PolicySearch(ConfiguredEmbeddings(), version=args.index_version,
                          threshold=args.threshold).search(args.query, category=args.category, doc_types=args.doc_type, k=args.k)
    print(json.dumps(sanitize_data(result), indent=2))
    return 0


def cmd_support(args):
    import json
    from capstone_agent.support.runtime import run_support,MEMORY
    from capstone_agent.support.registry import SessionIdentity
    faults={}
    if args.fault_tracking_timeout:faults['get_tracking_events']='TIMEOUT'
    if args.fault_escalation_fail:faults['create_escalation']='FAILED'
    if args.fault_model:faults['supervisor']='FAILED'
    if not args.chat and not args.message.strip():raise ValueError('A question or --chat is required.')
    identity=SessionIdentity(args.customer);search=None
    def ask(message):
        nonlocal search
        if not message.strip().startswith(('/reset','/feedback','/forget-preferences')) and search is None:
            from capstone_agent.retrieval.configured_embeddings import ConfiguredEmbeddings
            from capstone_agent.retrieval.chroma_store import PolicySearch
            search=PolicySearch(ConfiguredEmbeddings());search.search('return policy')
        result=run_support(message,identity=identity,search=search,faults=faults,
                           memory_enabled=False if args.no_memory else None)
        print(json.dumps({k:result.get(k) for k in ['response','outcome','ticket','triggers','refusals','model_calls','tool_calls','memory','style']},indent=2))
    if not args.chat:
        ask(args.message)
        from capstone_agent.observability.support_tracing import EXPORTER
        EXPORTER.wait(5)
        return 0
    print('Synthetic support chat. /reset clears context; /feedback too_long|too_short|unclear|helpful|not_helpful|enable|disable|reset_style; /forget-preferences deletes style data; /quit exits. Explicit feedback enables style learning; two matching signals adapt style. Preferences persist locally; session memory is lost on restart.')
    try:
        while True:
            try:message=input('You: ')
            except EOFError:break
            if message.strip() in {'/quit','/exit'}:break
            if message.strip():ask(message)
    finally:
        MEMORY.reset(identity)
        from capstone_agent.observability.support_tracing import EXPORTER
        EXPORTER.wait(5)
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
    from capstone_agent.prompts.templates import DEFAULT_VARIANT
    llm.add_argument("--prompt", choices=["A", "B", "C"], default=DEFAULT_VARIANT,
                     help="v3 development default C; A/B remain available for comparison")
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
    evaluate = sub.add_parser("evaluate", help="DeepEval checks on saved outputs; local results")
    evaluate.add_argument("run_dir")
    evaluate.add_argument("--judge-env-file", help="explicit separate judge provider config; enables LLM scoring")
    evaluate.add_argument("--case", action="append")
    evaluate.set_defaults(func=cmd_evaluate)
    ingest_p = sub.add_parser("ingest", help="Build the configured local policy index")
    ingest_p.add_argument("--index-version", default="v2")
    ingest_p.set_defaults(func=cmd_ingest)
    search = sub.add_parser("search-policy", help="Retrieve cited policy passages locally")
    search.add_argument("query")
    search.add_argument("--index-version", help="Default: calibrated configured index")
    search.add_argument("--category", choices=["footwear", "apparel", "home", "electronics", "perishable_grocery"])
    search.add_argument("--doc-type", action="append", help="Repeat to filter document IDs")
    search.add_argument("--k", type=int, default=5)
    search.add_argument("--threshold", type=float, help="Override the calibrated local threshold")
    search.set_defaults(func=cmd_search_policy)
    final_eval=sub.add_parser('evaluate-support',help='Record final-agent runs and DeepEval code contracts; semantic grading remains separate')
    final_eval.add_argument('--dataset',required=True)
    final_eval.add_argument('--contexts',help='Reviewed case-ID to customer_id/setup_turns mapping')
    final_eval.add_argument('--output',default='artifacts/final_support_evaluation')
    final_eval.add_argument('--repeats',type=int,default=1)
    final_eval.add_argument('--dry-run',action='store_true')
    final_eval.add_argument('--allow-holdout',action='store_true')
    final_eval.set_defaults(func=cmd_evaluate_support)
    doctor = sub.add_parser('doctor',help='Validate configuration and local assets without printing values')
    doctor.add_argument('--index',action='store_true',help='Also load pinned embeddings and verify the current index')
    doctor.set_defaults(func=cmd_doctor)
    support = sub.add_parser('support', help='Multi-agent support with session memory and style feedback; synthetic data/mock handoff only')
    support.add_argument('message',nargs='?',default='')
    support.add_argument('--chat',action='store_true',help='Keep one synthetic session; /reset, /feedback, /forget-preferences and /quit supported')
    support.add_argument('--no-memory',action='store_true',help='Disable retained context for comparison')
    support.add_argument('--customer',choices=['C-100','C-101','C-102','C-103'],default='C-100',help='Select synthetic account before the request')
    support.add_argument('--fault-tracking-timeout',action='store_true')
    support.add_argument('--fault-escalation-fail',action='store_true')
    support.add_argument('--fault-model',action='store_true')
    support.set_defaults(func=cmd_support)
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
