"""Minimize support packets; keep raw order/customer IDs out of operational records."""
import hashlib
import re
from capstone_agent.safety.redaction import sanitize

PHONE = re.compile(r'(?<!\w)(?:\+?\d[\d ()-]{7,}\d)(?!\w)')
ADDRESS = re.compile(r'\b\d{1,6}\s+(?:[A-Za-z]+\s+){0,5}(?:Street|St|Road|Rd|Avenue|Ave|Lane|Ln|Drive|Dr|Way|Boulevard|Blvd)\b\.?', re.I)
IDENTIFIER = re.compile(r'\b(?:O-\d{4}|C-\d{3})\b', re.I)

def opaque(value: str):
    return 'ref:' + hashlib.sha256(value.encode()).hexdigest()[:20]

def mask_sensitive(text: str, secrets=()):
    text = sanitize(text, secrets)
    text = PHONE.sub(lambda m: m.group() if re.fullmatch(r'\d{4}-\d{2}-\d{2}', m.group()) else '[REDACTED-PHONE]', text)
    text = ADDRESS.sub('[REDACTED-ADDRESS]', text)
    return text

def minimize(text: str, secrets=()):
    return IDENTIFIER.sub(lambda m: opaque(m.group().upper()), mask_sensitive(text, secrets))
