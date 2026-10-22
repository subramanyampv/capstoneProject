"""Minimize support packets; keep raw order/customer IDs out of operational records."""
import hashlib
import re
from datetime import datetime
from capstone_agent.safety.redaction import sanitize

PHONE = re.compile(r'(?<!\w)(?:\+?\d[\d ()-]{7,}\d)(?!\w)')
ADDRESS = re.compile(r'\b\d{1,6}\s+(?:[A-Za-z]+\s+){0,5}(?:Street|St|Road|Rd|Avenue|Ave|Lane|Ln|Drive|Dr|Way|Boulevard|Blvd)\b\.?', re.I)
IDENTIFIER = re.compile(r'\b(?:O-\d{4}|C-\d{3})\b', re.I)

def opaque(value: str):
    return 'ref:' + hashlib.sha256(value.encode()).hexdigest()[:20]

def mask_sensitive(text: str, secrets=(), *, verified_ticket_ids=()):
    # Only callers with actual verified tool results may supply this allowlist.
    # A customer-written MOCK prefix must never exempt a phone number from masking.
    protected={};index=0
    for reference in sorted(set(verified_ticket_ids)):
        if not re.fullmatch(r'MOCK-[a-f0-9]{12}',reference) or any(secret and secret in reference for secret in secrets):continue
        token=chr(0xE000+index);index+=1
        while token in text or any(secret and secret in token for secret in secrets):
            token=chr(0xE000+index);index+=1
        text=text.replace(reference,token);protected[token]=reference
    text = sanitize(text, secrets)
    def phone_or_timestamp(match):
        value=match.group()
        # A rendered tracking timestamp contains a space before its hour.
        # The phone pattern stops at the first colon, so validate the complete
        # adjacent clock/zone before retaining that date/hour prefix.
        if re.fullmatch(r'\d{4}-\d{2}-\d{2}',value):
            try:
                datetime.fromisoformat(value)
                return value
            except ValueError:
                pass
        if re.fullmatch(r'\d{4}-\d{2}-\d{2} \d{2}',value):
            clock=re.match(r':\d{2}(?::\d{2})?(?:[ \t]*(?:UTC|GMT|Z)|[+-]\d{2}:?\d{2})(?!\w)',
                           text[match.end():],re.I)
            if clock:
                suffix=re.sub(r'\s*(?:UTC|GMT|Z)$','+00:00',clock.group(),flags=re.I)
                try:
                    datetime.fromisoformat(value+suffix)
                    return value
                except ValueError:
                    pass
        return '[REDACTED-PHONE]'
    text = PHONE.sub(phone_or_timestamp, text)
    text = ADDRESS.sub('[REDACTED-ADDRESS]', text)
    for token,reference in protected.items():text=text.replace(token,reference)
    return text

def minimize(text: str, secrets=(), *, verified_ticket_ids=()):
    return IDENTIFIER.sub(lambda m: opaque(m.group().upper()), mask_sensitive(text, secrets,verified_ticket_ids=verified_ticket_ids))
