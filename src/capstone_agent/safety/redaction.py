"""Pattern-based minimization plus exact configured-secret removal; not universal PII detection."""

import re

PATTERNS = [
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    re.compile(r"(?<!\d)(?:\d[ -]?){13,19}(?!\d)"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{8,}\b"),
    re.compile(r"\bBearer\s+\S+", re.I),
    re.compile(r"\b(?:api[_ -]?key|password|secret|token)\s*[:=]\s*[^\s,;]+", re.I),
    re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
]


def sanitize(text: str, secrets: tuple[str, ...] = ()) -> str:
    for secret in secrets:
        if secret:
            text = text.replace(secret, "[REDACTED-SECRET]")
    for pattern in PATTERNS:
        text = pattern.sub("[REDACTED-PII]", text)
    return text


def sanitize_data(value, secrets: tuple[str, ...] = ()):
    if isinstance(value, str):
        return sanitize(value, secrets)
    if isinstance(value, list):
        return [sanitize_data(item, secrets) for item in value]
    if isinstance(value, dict):
        return {key: sanitize_data(item, secrets) for key, item in value.items()}
    return value
