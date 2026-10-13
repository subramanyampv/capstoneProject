"""Small policy-context hints from public catalog metadata; never policy authority."""

import re

PROFILE = "policy-context-v1"
POLICY_TOPIC = re.compile(r"\b(return\w*|refund\w*|cancel\w*|warrant\w*|shipping)\b|\bsend\b.+\bback\b", re.I)


def expand_query(query, catalog, *, category=None):
    hints = []
    if POLICY_TOPIC.search(query):
        categories = set()
        for product in catalog:
            # Resolve the catalog's distinctive leading name, including the
            # ordinary plural (TrailRunner/TrailRunners), without using case IDs.
            name = product["name"].split()[0]
            if len(name) >= 6 and re.search(r"\b" + re.escape(name) + r"s?\b", query, re.I):
                categories.add(product["category"])
        if category in {product["category"] for product in catalog}:
            categories.add(category)
        hints.extend("Product category: " + value + "." for value in sorted(categories))
        if re.search(r"\bexceptions?\b", query, re.I):
            hints.append("Return policy exception, ineligible returns human review.")
    requested_human = (re.search(r"\b(representative|supervisor)\b", query, re.I)
                       or re.search(r"\b(want|need|speak|talk|connect|contact|request|reach)\b.{0,50}\bhuman\b(?!\s+review)", query, re.I)
                       or re.search(r"\bhuman\s+(agent|support)\b", query, re.I))
    bypass_review = re.search(r"\b(without|skip|avoid|bypass|no)\b.{0,30}\b(human|review)\b", query, re.I)
    if requested_human and not bypass_review:
        hints.append("Escalation guidelines human requests.")
    return query + (" " + " ".join(hints) if hints else ""), hints
