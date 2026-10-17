"""Minimize textual evidence before serialization, preserving numeric JSON types."""
import json
from capstone_agent.support.privacy import minimize


def verified_tickets(result):
    """IDs backed by successful code tool envelopes, never model prose alone."""
    ticket=result.get('ticket') or {}
    if ticket.get('status')!='created':return ()
    ident=ticket.get('ticket_id')
    if not isinstance(ident,str):return ()
    return (ident,) if any(row.get('name')=='create_escalation' and row.get('status')=='ok'
        and (row.get('data') or {}).get('ticket_id')==ident and row['data'].get('status')=='created'
        for row in result.get('tool_records',[])) else ()


def minimized_json(value, secrets=(), *, verified_ticket_ids=()):
    def clean(item):
        if isinstance(item,str):return minimize(item,secrets,verified_ticket_ids=verified_ticket_ids)
        if isinstance(item,list):return [clean(part) for part in item]
        if isinstance(item,dict):return {minimize(key,secrets):clean(part) for key,part in item.items()}
        return item
    return json.dumps(clean(value),allow_nan=False)
