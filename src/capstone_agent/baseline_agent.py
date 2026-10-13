"""Phase 2 — rule-based single-agent baseline.

Deliberately dumb and deterministic: keyword/regex intent matching over frozen
thresholds (`data/policy_rules.json`) and synthetic records, with template answers.
This is the measured starting point the later stages (LLM, RAG, tools, orchestration)
must beat — it is NOT the final architecture. The baseline intentionally exhibits the
two required limitations (paraphrase failure, multi-intent failure); they are asserted
in tests/unit/test_baseline_agent.py and analyzed in docs/baseline_limitations.md.

Run:  scripts/run_baseline.sh   |   python -m capstone_agent.baseline_agent --demo
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import uuid
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Callable

REPO_ROOT = Path(__file__).resolve().parents[2]

ORDER_ID_RE = re.compile(r"\bO[- ]?(\d{4})\b", re.IGNORECASE)
DAYS_AGO_RE = re.compile(r"\b(\d{1,3})\s*(?:day|days)\s*(?:ago|before that)\b")
SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
CARD_RE = re.compile(r"\b\d{13,19}\b")


def redact(text: str) -> str:
    """Minimize sensitive values BEFORE anything is logged (invariant)."""
    text = SSN_RE.sub("[REDACTED-PII]", text)
    return CARD_RE.sub("[REDACTED-PII]", text)


@dataclass
class BaselineResult:
    request_id: str
    intent: str
    matched: bool
    response: str
    latency_ms: float


@dataclass
class DataBundle:
    rules: dict
    orders: dict  # order_id -> record
    events: dict  # order_id -> list[event]
    catalog: dict  # sku -> product
    catalog_by_name: dict = field(default_factory=dict)
    catalog_version: str = ""

    @classmethod
    def load(cls, root: Path = REPO_ROOT) -> "DataBundle":
        def _json(name: str) -> dict:
            return json.loads((root / "data" / name).read_text())

        rules = _json("policy_rules.json")
        orders_raw = _json("sample_orders.json")
        events_raw = _json("sample_tracking_events.json")
        catalog_raw = _json("product_catalog.json")
        orders = {o["order_id"]: o for o in orders_raw["orders"]}
        catalog = {p["sku"]: p for p in catalog_raw["products"]}
        return cls(
            rules=rules,
            orders=orders,
            events=events_raw["events"],
            catalog=catalog,
            catalog_by_name={p["name"].lower(): p for p in catalog_raw["products"]},
            catalog_version=catalog_raw["version"],
        )


# ---------------------------------------------------------------- intent rules
# Ordered: first match wins. This ordering is also why multi-intent inputs fail —
# only one intent can ever be selected (demonstrated limitation #2).
INTENT_RULES: list[tuple[str, re.Pattern[str]]] = [
    ("feedback_style", re.compile(r"\b(too verbose|too long|too short|make (it|the answer|that) short\w*|shorter|more detail\w*)\b", re.I)),
    ("escalation_request", re.compile(r"\b(human|representative|supervisor|manager|speak to someone|escalate)\b", re.I)),
    ("cancellation", re.compile(r"\b(cancell?|don'?t want (it|the order))\b", re.I)),
    ("return_eligibility", re.compile(r"\b(returns?|returned|send (it|this|these|the \w+[- ]\w*)? ?back|exchange)\b", re.I)),
    ("refund_request", re.compile(r"\b(refund|money back|get my money)\b", re.I)),
    ("warranty", re.compile(r"\bwarrant\w*\b", re.I)),
    ("shipping_tracking", re.compile(r"\b(where is|track\w*|status|shipped|dispatched|deliver\w*\s*(yet|ed)?|arriv\w*|delay\w*|ETA)\b", re.I)),
    ("product_information", re.compile(r"\b(size|sizes|fit|true to size|material|wash\w*|care|spec\w*|compatibl\w*|color|do you (sell|have))\b", re.I)),
]


def detect_intent(message: str) -> tuple[str | None, bool]:
    for name, pattern in INTENT_RULES:
        if pattern.search(message):
            return name, True
    return "fallback", False


# ---------------------------------------------------------------- handlers
def _find_order(message: str, data: DataBundle) -> dict | None:
    m = ORDER_ID_RE.search(message)
    if not m:
        return None
    return data.orders.get(f"O-{m.group(1)}")


def _days_since(d: str | None, today: date) -> int | None:
    if not d:
        return None
    return (today - date.fromisoformat(d)).days


def handle_return(message: str, order: dict | None, data: DataBundle, today: date) -> str:
    if order is None:
        m = DAYS_AGO_RE.search(message)
        if m:
            days = int(m.group(1))
            window = data.rules["return_window_days"]["default"]
            verdict = "may be" if days <= window else "is likely outside"
            return (
                f"Without a verified order record I can only apply the default {window}-day window: "
                f"{days} days {verdict} eligible. Please provide your order number (e.g., O-1234) "
                f"for a verified decision. (config: data/policy_rules.json v{data.rules['version']})"
            )
        return "I need your order number (e.g., O-1234) to check return eligibility against verified records."
    if order["status"] != "delivered" or not order["delivered_on"]:
        return (
            f"Order {order['order_id']} has not been delivered yet (status: {order['status']}), "
            f"so the return window has not started. (source: data/sample_orders.json)"
        )
    days = _days_since(order["delivered_on"], today)
    rules = data.rules
    category = order["category"]
    if category in rules["return_excluded_categories"]:
        return (
            f"Order {order['order_id']} ({order['item_name']}) is in category '{category}', "
            f"which is excluded from returns by rule. No refund or return action can be offered; "
            f"a human-review path will be available with escalation (Phase 5). "
            f"(config: data/policy_rules.json v{rules['version']})"
        )
    window = rules["return_window_days"].get(category, rules["return_window_days"]["default"])
    inclusive = rules["return_window_inclusive"]
    within = days <= window if inclusive else days < window
    state = (
        f"ELIGIBLE: {days} days since delivery, within the {window}-day {category} window"
        if within
        else f"NOT ELIGIBLE: {days} days since delivery, outside the {window}-day {category} window"
    )
    action_note = (
        "Note: this rule-based baseline cannot create the return — simulated actions with "
        "confirmation gates arrive in Phase 5."
        if within
        else "If you believe an exception applies, a human-review path will arrive with escalation tooling."
    )
    return (
        f"Order {order['order_id']} ({order['item_name']}) was delivered {order['delivered_on']}. "
        f"{state}. {action_note} (sources: data/sample_orders.json, data/policy_rules.json v{rules['version']})"
    )


def handle_cancellation(message: str, order: dict | None, data: DataBundle, today: date) -> str:
    if order is None:
        return "I need your order number (e.g., O-1234) to check cancellation eligibility."
    allowed = data.rules["cancellation_allowed_statuses"]
    if order["status"] in allowed:
        return (
            f"Order {order['order_id']} is '{order['status']}' (not dispatched), so cancellation is "
            f"permitted by rule (cancellation_allowed_statuses: {allowed}). The baseline cannot execute "
            f"the cancellation itself — simulated writes behind an explicit confirmation gate arrive in Phase 5."
        )
    return (
        f"Order {order['order_id']} is '{order['status']}' — cancellation is only allowed while "
        f"{allowed}. Once dispatched, a return may be the path (I can check eligibility)."
    )


def handle_tracking(message: str, order: dict | None, data: DataBundle, today: date) -> str:
    if order is None:
        m = ORDER_ID_RE.search(message)
        if m:
            return (
                f"Order O-{m.group(1)} was not found in verified records. Please double-check the "
                f"order number — I will not guess a status without a record."
            )
        return "I need an order number (e.g., 'where is order O-1234') to look up verified tracking."
    events = data.events.get(order["order_id"], [])
    latest = events[-1] if events else None
    if latest:
        gap = _days_since(latest["timestamp"][:10], today)
        stale = f" No carrier event for {gap} days — treat this as stale." if gap >= 5 else ""
        return (
            f"Order {order['order_id']}: status '{order['status']}'. Latest tracking event: "
            f"'{latest['event']}' at {latest['location']} on {latest['timestamp']}."
            f"{stale} (source: data/sample_tracking_events.json; estimates are not guarantees.)"
        )
    return (
        f"Order {order['order_id']}: status '{order['status']}'. No carrier events yet "
        f"{'(placed ' + order['placed_on'] + ')' if order.get('placed_on') else ''}."
    )


def handle_product(message: str, order: dict | None, data: DataBundle, today: date) -> str:
    low = message.lower()
    product = next((p for name, p in data.catalog_by_name.items() if name.split()[0] in low), None)
    if product is None and order:
        product = data.catalog.get(order["item_sku"])
    if product is None:
        return "Which product do you mean? I can answer sizing, materials, and care from the catalog."
    if re.search(r"\bwash|care\b", low):
        text = f"{product['name']}: {product['care']}"
    elif re.search(r"\bmaterial", low):
        text = f"{product['name']}: {product['material'] or 'material not specified in the catalog — disclosed as missing.'}"
    elif re.search(r"\bsize|fit|true to size", low):
        if product["sizes"] is None:
            text = f"{product['name']}: no size specification exists in the catalog — I won't invent one."
        else:
            note = f" {product['sizing_note']}" if product["sizing_note"] else ""
            text = f"{product['name']} comes in sizes {product['sizes']}.{note}"
    else:
        text = f"{product['name']} (category {product['category']}, ${product['price_usd']})."
    return text + f" (source: data/product_catalog.json v{data.catalog_version})"


def handle_warranty(message: str, order: dict | None, data: DataBundle, today: date) -> str:
    category = order["category"] if order else None
    if category is None:
        return "Which order or product? Warranty depends on category."
    days = data.rules["warranty_days"].get(category)
    if days == 0:
        return f"{category} items carry no warranty. (config: data/policy_rules.json v{data.rules['version']})"
    return (
        f"{'Order ' + order['order_id'] + ' (' + order['item_name'] + ')' if order else category} "
        f"carries a {days}-day warranty. (config: data/policy_rules.json v{data.rules['version']})"
    )


def handle_refund(message: str, order: dict | None, data: DataBundle, today: date) -> str:
    if order is None:
        return "I need your order number to check refund eligibility against verified records."
    threshold = data.rules["refund_auto_approve_max_amount"]
    if order["amount_usd"] > threshold:
        return (
            f"Order {order['order_id']} is ${order['amount_usd']} — above the ${threshold} auto-approve "
            f"threshold, so it requires human review. The baseline cannot create the escalation ticket "
            f"yet (Phase 5 mock queue)."
        )
    return handle_return(message, order, data, today)


def handle_feedback(_: str, __: dict | None, data: DataBundle, today: date) -> str:
    return (
        "Noted. This rule-based baseline has no adaptation module — every answer uses the same "
        "template length. Controlled feedback categories and whitelisted style adjustment arrive in Phase 7."
    )


def handle_escalation(_: str, __: dict | None, data: DataBundle, today: date) -> str:
    return (
        "I can't create a human-handoff ticket in this baseline (no escalation tool yet, Phase 5). "
        "If your issue involves injury, a denied policy exception, or conflicting policies, "
        "that will route automatically once the safety gateway is in place."
    )


def handle_fallback(_: str, __: dict | None, data: DataBundle, today: date) -> str:
    return (
        "Sorry — I didn't understand that request. This assistant matches fixed phrases and can "
        "help with: order status, tracking, returns, refunds, cancellation, product info, warranty. "
        "Try rephrasing with an order number, e.g. 'Where is order O-1234?'"
    )


HANDLERS: dict[str, Callable] = {
    "return_eligibility": handle_return,
    "cancellation": handle_cancellation,
    "shipping_tracking": handle_tracking,
    "product_information": handle_product,
    "warranty": handle_warranty,
    "refund_request": handle_refund,
    "feedback_style": handle_feedback,
    "escalation_request": handle_escalation,
    "fallback": handle_fallback,
}


def respond(message: str, today: date | None = None, data: DataBundle | None = None) -> BaselineResult:
    today = today or date.today()
    data = data or DataBundle.load()
    start = time.perf_counter()
    intent, matched = detect_intent(message)
    order = _find_order(message, data)
    response = HANDLERS[intent](message, order, data, today)
    latency_ms = round((time.perf_counter() - start) * 1000, 2)
    return BaselineResult(uuid.uuid4().hex[:12], intent, matched, response, latency_ms)


def log_line(result: BaselineResult, message: str) -> str:
    return json.dumps(
        {
            "ts": date.today().isoformat() + f"T{time.strftime('%H:%M:%S')}",
            "request_id": result.request_id,
            "intent": result.intent,
            "matched": result.matched,
            "latency_ms": result.latency_ms,
            "input": redact(message),
            "response_chars": len(result.response),
        }
    )


DEMO_SEQUENCE = [
    ("success: order status", "Where is my order O-1003? Has it shipped?"),
    ("success: return eligibility (canonical demo input)", "I received my shoes (order O-1001) 12 days ago. Can I return them?"),
    ("LIMITATION 1 - paraphrase failure expected", "Am I able to send these trainers back? A fortnight has passed since I got them."),
    ("LIMITATION 2 - multi-intent failure expected", "Where is order O-1002 and can I return the jacket if it arrives late?"),
    ("success: boundary outside window", "Can I return order O-1005? It was delivered a while ago."),
    ("success: unknown order handled", "track order O-9999"),
    ("success: cancellation eligibility", "Cancel my order O-1003."),
    ("success: product info", "What sizes do the TrailRunner Shoes come in?"),
]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="baseline_agent", description=__doc__)
    parser.add_argument("--demo", action="store_true", help="run the fixed scripted sequence")
    parser.add_argument("--ask", metavar="TEXT", help="answer a single message")
    parser.add_argument("--today", metavar="YYYY-MM-DD", help="scenario clock for deterministic evidence runs")
    parser.add_argument("--log", metavar="PATH", help="append sanitized JSONL log lines")
    args = parser.parse_args(argv)

    today = date.fromisoformat(args.today) if args.today else None
    log_path = Path(args.log) if args.log else None

    def run(msg: str) -> BaselineResult:
        result = respond(msg, today=today)
        print(f"\nIN : {msg}\nOUT: {result.response}\n     intent={result.intent} matched={result.matched} latency={result.latency_ms}ms")
        if log_path:
            with log_path.open("a") as fh:
                fh.write(log_line(result, msg) + "\n")
        return result

    if args.ask:
        run(args.ask)
    elif args.demo:
        for label, msg in DEMO_SEQUENCE:
            print(f"\n=== {label} ===")
            run(msg)
        print(f"\nScenario clock: {today or date.today()}  |  data versions: policy_rules v{DataBundle.load().rules['version']}")
    else:
        print("Interactive baseline (Ctrl-D to exit). Type a customer question:")
        try:
            while True:
                run(input("> "))
        except EOFError:
            pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
