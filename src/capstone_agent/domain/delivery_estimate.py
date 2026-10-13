"""Deterministic delivery estimates from explicit distance/weather facts and demo rules."""

import json
import math
from datetime import date, timedelta
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

ROOT = Path(__file__).resolve().parents[3]


class DeliveryRules(BaseModel):
    model_config = ConfigDict(extra="forbid")
    version: str = Field(min_length=1)
    scope: str
    miles_per_transit_block: float = Field(gt=0, allow_inf_nan=False)
    days_per_transit_block: int = Field(ge=1, le=30)
    minimum_transit_days: int = Field(ge=1, le=30)
    disruption_delay_days: int = Field(ge=0, le=30)
    upper_buffer_days: int = Field(ge=0, le=30)
    day_basis: Literal["calendar"]


class DeliveryFacts(BaseModel):
    model_config = ConfigDict(extra="forbid")
    destination: str = Field(min_length=1, max_length=100)
    dispatch_date: date | None
    distance_miles: float | None = Field(ge=0, le=25000, allow_inf_nan=False)
    weather: Literal["clear", "no_disruption_alert", "storm", "snow", "storm_and_snow", "unknown"]
    distance_source: str | None
    weather_source: str | None
    observed_on: date

    @model_validator(mode="after")
    def dates_and_sources(self):
        if self.distance_miles is not None and not self.distance_source:
            raise ValueError("Distance requires a source.")
        if self.weather != "unknown" and not self.weather_source:
            raise ValueError("Known weather requires a source.")
        if self.dispatch_date and self.dispatch_date > self.observed_on:
            raise ValueError("Dispatch is unverified when its date is in the future.")
        return self


def estimate_delivery(facts: DeliveryFacts, *, today: date, rules_path: Path | None = None) -> dict:
    path = rules_path or ROOT / "data/delivery_estimate_rules.json"
    rules = DeliveryRules.model_validate(json.loads(path.read_text())).model_dump()
    result = {"destination": facts.destination, "rule_version": rules["version"],
              "rule_source": "data/delivery_estimate_rules.json", "guaranteed": False,
              "distance_source": facts.distance_source, "weather_source": facts.weather_source,
              "status": "insufficient_evidence", "earliest": None, "latest": None}
    if facts.observed_on != today:
        return {**result, "reason": "Facts are stale or future-dated; refresh them before estimating."}
    if facts.dispatch_date is None or facts.distance_miles is None or facts.weather == "unknown":
        return {**result, "reason": "Verified dispatch, sourced distance, and known weather are required."}
    base = max(rules["minimum_transit_days"], math.ceil(
        facts.distance_miles * rules["days_per_transit_block"] / rules["miles_per_transit_block"]))
    # One disruption increment, even if storm and snow describe the same event.
    delay = rules["disruption_delay_days"] if facts.weather in {"storm", "snow", "storm_and_snow"} else 0
    start = facts.dispatch_date + timedelta(days=base + delay)
    end = start + timedelta(days=rules["upper_buffer_days"])
    if end < today:
        return {**result, "status": "needs_review", "reason": "Estimated window elapsed; obtain fresh carrier tracking."}
    return {**result, "status": "estimated", "earliest": max(start, today).isoformat(),
            "latest": end.isoformat(), "base_days": base, "weather_delay_days": delay,
            "reason": "Synthetic calendar-day rule estimate; carrier handling and routing may differ."}
