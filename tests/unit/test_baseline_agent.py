"""Phase 2 baseline tests: deterministic rule behavior on the frozen clock 2026-10-12,
plus permanent assertions that the two REQUIRED limitations actually occur
(so the demo evidence can never silently regress)."""

import json
import re
from datetime import date

import pytest

from capstone_agent.baseline_agent import DataBundle, log_line, redact, respond

TODAY = date(2026, 10, 12)  # scenario clock; O-1001 = 12d, O-1005 = 31d, boundary = exactly 30d


@pytest.fixture(scope="module")
def data() -> DataBundle:
    return DataBundle.load()


def ask(msg: str):
    return respond(msg, today=TODAY)


class TestReturnEligibility:
    def test_within_window(self):
        r = ask("Can I return order O-1001?")
        assert r.intent == "return_eligibility"
        assert "ELIGIBLE" in r.response and "12 days" in r.response

    def test_outside_window(self):
        r = ask("Can I return order O-1005?")
        assert "NOT ELIGIBLE" in r.response and "31 days" in r.response

    def test_boundary_exactly_30_days_is_inclusive(self):
        # O-1005 delivered 2026-09-11; exactly 30 days later is 2026-10-11.
        r = respond("Can I return order O-1005?", today=date(2026, 10, 11))
        assert "ELIGIBLE" in r.response and "30 days" in r.response

    def test_excluded_category(self):
        r = ask("Can I return the cheese box, order O-1004?")
        assert "excluded from returns" in r.response

    def test_not_delivered_no_window_start(self):
        r = ask("Can I return order O-1002?")
        assert "has not been delivered" in r.response

    def test_unknown_order_no_guessing(self):
        r = ask("Can I return order O-9999?")
        assert r.intent == "return_eligibility"
        # falls to the no-record clarification path (order lookup miss => ask for number)
        assert "need your order number" in r.response or "not found" in r.response


class TestCancellationAndTracking:
    def test_cancellable_pre_dispatch(self):
        r = ask("Cancel my order O-1003.")
        assert r.intent == "cancellation" and "permitted by rule" in r.response

    def test_not_cancellable_after_dispatch(self):
        r = ask("cancel order O-1001")
        assert "only allowed while" in r.response

    def test_latest_event_returned(self):
        r = ask("where is order O-1002?")
        assert r.intent == "shipping_tracking"
        assert "arrived_sorting_facility" in r.response and "2026-10-05" in r.response
        assert "stale" in r.response  # 7 days without events

    def test_unknown_order_id(self):
        r = ask("track order O-9999")
        assert "not found" in r.response


class TestRequiredLimitations:
    def test_paraphrase_failure_is_demonstrated(self):
        r = ask("Am I able to send these trainers back? A fortnight has passed since I got them.")
        assert r.intent == "fallback" and r.matched is False

    def test_multi_intent_failure_is_demonstrated(self):
        r = ask("Where is order O-1002 and can I return the jacket if it arrives late?")
        # First rule wins: return handled, the tracking question is silently dropped.
        assert r.intent == "return_eligibility"
        assert "tracking" not in r.response.lower() and "Latest tracking event" not in r.response


class TestLoggingSafety:
    def test_ssn_and_card_redacted_in_log_lines(self):
        msg = "my ssn is 123-45-6789 and card 4111111111111111 — where is order O-1003"
        line = log_line(respond(msg, today=TODAY), msg)
        assert "123-45-6789" not in line and "4111111111111111" not in line
        assert "[REDACTED-PII]" in line

    def test_redact_unit(self):
        assert redact("123-45-6789") == "[REDACTED-PII]"

    def test_log_line_is_jsonl(self):
        line = log_line(ask("track order O-1001"), "track order O-1001")
        assert re.match(r"^\{.*\}$", line)
        parsed = json.loads(line)
        assert set(parsed) >= {"ts", "request_id", "intent", "matched", "latency_ms", "input"}
