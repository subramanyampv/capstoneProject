"""Validate versioned Markdown, enforce rule facts and produce deterministic chunks."""

import hashlib
import re
from datetime import date
from pathlib import Path

import yaml

REQUIRED_DOCS = {"return_policy", "refund_policy", "shipping_policy", "cancellation_policy",
                 "warranty_policy", "faq", "escalation_guidelines"}
REQUIRED_META = {"doc_id", "title", "version", "effective_date", "authority", "owner"}
CATEGORIES = ("footwear", "apparel", "home", "electronics", "perishable_grocery")
METADATA_PROFILE = "section-category-applicability-v1"


def load_corpus(directory: Path):
    chunks, hashes, quarantined = [], {}, []
    seen = set()
    for path in sorted(directory.glob("*.md")):
        text = path.read_text()
        parts = text.split("---", 2)
        try:
            if len(parts) != 3 or parts[0].strip():
                raise ValueError("missing_front_matter")
            meta = yaml.safe_load(parts[1])
            if not isinstance(meta, dict) or not REQUIRED_META <= meta.keys():
                raise ValueError("missing_metadata")
            if any(not isinstance(meta[key], str) or not meta[key].strip() for key in REQUIRED_META):
                raise ValueError("invalid_metadata")
            date.fromisoformat(meta["effective_date"])
            if meta["authority"] not in {"policy", "faq"}:
                raise ValueError("invalid_authority")
            scopes = meta.get("section_categories", {})
            if not isinstance(scopes, dict) or any(
                not isinstance(section, str) or not isinstance(values, list) or not values
                or any(not isinstance(value, str) or value not in CATEGORIES for value in values)
                or len(values) != len(set(values)) for section, values in scopes.items()
            ):
                raise ValueError("invalid_category_scope")
            headings = {re.sub(r"[^a-z0-9]+", "-", heading.lower()).strip("-")
                        for heading in re.findall(r"^##\s+(.+)$", parts[2], flags=re.M)}
            if not set(scopes) <= headings:
                raise ValueError("unknown_category_section")
            key = (meta["doc_id"], meta["version"])
            if key in seen:
                raise ValueError("duplicate_document_version")
            seen.add(key)
        except (ValueError, yaml.YAMLError):
            quarantined.append({"file": path.name, "reason": "invalid_front_matter"})
            continue
        hashes[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
        body = parts[2].strip()
        sections = re.split(r"^##\s+(.+)$", body, flags=re.M)
        for index in range(1, len(sections), 2):
            heading, content = sections[index], sections[index + 1].strip()
            section = re.sub(r"[^a-z0-9]+", "-", heading.lower()).strip("-")
            if not content:
                continue
            # Conservative byte bound; this corpus fits whole sections. Fail rather
            # than silently truncate if authoring exceeds the declared small-corpus limit.
            if len(content.encode()) > 2400:
                raise ValueError("Section too long; split into smaller authored sections.")
            record = {"doc_id": meta["doc_id"], "version": meta["version"],
                      "section_id": section, "effective_date": meta["effective_date"],
                      "authority": meta["authority"], "rule_version": str(meta.get("rule_version", "")),
                      "evaluation_conflict": str(meta.get("evaluation_conflict", "")),
                      "content_hash": hashlib.sha256(content.encode()).hexdigest(),
                      "instruction_flag": bool(re.search(r"ignore (?:previous|all) instructions", content, re.I))}
            categories = scopes.get(section, list(CATEGORIES))
            record["category"] = "all" if set(categories) == set(CATEGORIES) else ",".join(sorted(categories))
            record.update({f"applies_{category}": category in categories for category in CATEGORIES})
            if meta.get("superseded_on"):
                record["superseded_on"] = date.fromisoformat(str(meta["superseded_on"])).isoformat()
            chunks.append({"id": f"{meta['doc_id']}:{meta['version']}:{section}:0",
                           "text": heading + "\n" + content, "metadata": record})
    ids = [chunk["id"] for chunk in chunks]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate section chunk IDs.")
    return chunks, hashes, quarantined


def check_rule_consistency(chunks, rules):
    sections = {(c["metadata"]["doc_id"], c["metadata"]["section_id"]): c["text"] for c in chunks}
    if {c["metadata"]["doc_id"] for c in chunks} != REQUIRED_DOCS:
        raise ValueError("The seven required policy documents must all be present.")
    if any(c["metadata"]["rule_version"] != rules["version"] for c in chunks):
        raise ValueError("Corpus rule version mismatch.")
    window = sections[("return_policy", "window")]
    expected = {"default": "default return window is", "footwear": "Footwear and apparel have",
                "apparel": "Footwear and apparel have", "home": "home products have", "electronics": "electronics have"}
    for category, prefix in expected.items():
        if not re.search(re.escape(prefix) + rf" {rules['return_window_days'][category]}[- ]day", window, re.I):
            # Default is expressed as "30 days", also covered by [- ]day.
            raise ValueError("Return window text differs from configured rules.")
    if not rules["return_window_inclusive"] or "inclusive" not in window:
        raise ValueError("Return boundary differs from configured rule.")
    if rules["return_excluded_categories"] != ["perishable_grocery"]:
        raise ValueError("Excluded category requires a corpus revision.")
    threshold = rules["refund_auto_approve_max_amount"]
    if f"threshold is ${threshold}" not in sections[("refund_policy", "review-threshold")]:
        raise ValueError("Refund threshold text differs from configured rules.")
    if f"{rules['restocking_fee_pct']['electronics_opened']}%" not in sections[("return_policy", "restocking")]:
        raise ValueError("Restocking fee text differs from configured rules.")
    warranty = sections[("warranty_policy", "durations")]
    for value in set(rules["warranty_days"].values()):
        if not re.search(rf"\b{value}[- ]days?\b", warranty):
            raise ValueError("Warranty duration text differs from configured rules.")
    if rules["cancellation_allowed_statuses"] != ["pending", "processing"]:
        raise ValueError("Cancellation statuses require a corpus revision.")
    shipping = sections[("shipping_policy", "transit-estimates")]
    low, high = rules["shipping_standard_days_estimate"]
    if f"{low} to {high} days" not in shipping or rules["shipping_guarantee"] or rules["international_shipping"]:
        raise ValueError("Shipping policy differs from configured rules.")
    # Only the explicitly marked electronics FAQ conflict is exempt from window consistency.
    faq = next(c for c in chunks if c["metadata"]["doc_id"] == "faq" and c["metadata"]["section_id"] == "electronics-returns")
    if faq["metadata"]["evaluation_conflict"] != "electronics_return_window":
        raise ValueError("R05 deliberate conflict must be labeled.")
