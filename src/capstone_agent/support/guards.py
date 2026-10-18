"""Versioned deterministic refusal/escalation checks and grounded final gates."""
import json
import re
from pathlib import Path
from capstone_agent.support.privacy import minimize
from capstone_agent.retrieval.grounded_answer import POLICY_NUMBER

ROOT=Path(__file__).resolve().parents[3]

class SafetyRules:
    def __init__(self,path=ROOT/'config/safety_rules.json'):
        self.raw=json.loads(path.read_text())
        if set(self.raw['refusals'])!={'R1','R2','R3','R4'} or set(self.raw['triggers'])!={'T1','T6'}:
            raise ValueError('INVALID_SAFETY_CONFIGURATION')
        expected={'tool_calls':8,'handoffs':4,'llm_calls':12,'specialist_steps':4,'escalation_steps':3,'replans':1,'structured_repairs':1}
        if self.raw['limits']!=expected: raise ValueError('UNSUPPORTED_SAFETY_LIMITS')
        self.refusals={k:[re.compile(p,re.I) for p in v] for k,v in self.raw['refusals'].items()}
        self.triggers={k:[re.compile(p,re.I) for p in v] for k,v in self.raw['triggers'].items()}
        self.legal=[re.compile(p,re.I) for p in self.raw['legal']]
        self.exception=[re.compile(p,re.I) for p in self.raw['exception']]
        self.version=self.raw['version']
    def match(self,text):
        refusals=[k for k,ps in self.refusals.items() if any(p.search(text) for p in ps)]
        triggers=[k for k,ps in self.triggers.items() if any(p.search(text) for p in ps)]
        return refusals,triggers,any(p.search(text) for p in self.legal)

REFUSAL='I cannot follow requests to bypass rules, disclose private information, save sensitive identifiers such as Social Security numbers, or provide medical/legal advice. I can help with supported order and policy questions.'
FAILURE='I could not confirm the handoff. Please contact the retailer support team directly; no ticket is confirmed.'
NO_ACTION_NEEDED=re.compile(r'\bno\s+(?:further|additional|more)\s+(?:(?:shipping|delivery|tracking)\s+)?(?:action|steps?|support|assistance)\s+(?:is\s+|are\s+)?(?:needed|required|necessary)\b',re.I)


def qualify_delivery_conclusion(draft):
    """Replace only the unsupported conclusion; preserve other claims and references.

    Callers must require verified current tracking and replay every final gate.
    This is not a general semantic correction or permission to assert receipt.
    """
    replacement='the carrier record does not establish whether further assistance is needed'
    repaired=draft.model_copy(deep=True)
    repaired.answer=NO_ACTION_NEEDED.sub(replacement,repaired.answer)
    repaired.why=[NO_ACTION_NEEDED.sub(replacement,v) for v in repaired.why]
    repaired.next_steps=[NO_ACTION_NEEDED.sub(replacement,v) for v in repaired.next_steps]
    repaired.why.append('Delivery statements describe the carrier record, not independent confirmation of receipt.')
    try:return type(draft).model_validate(repaired.model_dump())
    except ValueError:return None



def final_errors(draft, *, refs, facts, refusals, triggers, ticket, intents):
    errors=[]
    if not set(draft.intents_addressed)>=set(intents): errors.append('G5_INTENT_COVERAGE')
    cited={json.dumps(r.model_dump(),sort_keys=True) for r in draft.citations}
    if not cited<=refs: errors.append('G4_UNRESOLVED_CITATION')
    retrieved={json.dumps({'source_id':'doc:'+r['doc_id'],'section':r['section_id'],'record_version':r['version']},sort_keys=True)
        for fact in facts if fact['name']=='search_policy' for r in fact['data']['results']}
    if any(ref.source_id.startswith('doc:') and json.dumps(ref.model_dump(),sort_keys=True) not in retrieved for ref in draft.citations):
        errors.append('G4_POLICY_NOT_RETRIEVED')
    body=' '.join([draft.answer,*draft.why,*draft.next_steps])
    if NO_ACTION_NEEDED.search(body):
        errors.append('G3_UNSUPPORTED_NO_ACTION_NEEDED')
    if refusals and not re.search(r"cannot|can't|unable|decline|not (?:able|allowed)",body,re.I): errors.append('G2_REFUSAL')
    if triggers:
        if ticket and ticket.get('status')=='created':
            if ticket['ticket_id'] not in body: errors.append('G1_TICKET_MISSING')
        elif not re.search(r'could not confirm|not confirmed|handoff failed|unable to (?:create|confirm)',body,re.I):
            errors.append('G1_FAILURE_DISCLOSURE')
    action_claim=re.compile(r'\b(?:issued|processed|completed|approved|executed)\s+(?:your |the |a )?(?:refund|return|cancellation)\b|\b(?:refunded|cancelled|canceled)\s+(?:your|the)\s+order',re.I)
    future_claim=re.compile(r'\b(?:I|we)\s+(?:will|can|have already)\s+(?:issue|process|execute|approve|refund|cancel)\b|\b(?:your|the)\s+(?:refund|return|cancellation)\s+(?:has been|is|was)\s+(?:processed|issued|approved|completed|executed)\b',re.I)
    for match in [*action_claim.finditer(body),*future_claim.finditer(body)]:
        prefix=re.split(r'[.!?;]|\b(?:but|however|although|and|then)\b',body[:match.start()],flags=re.I)[-1][-50:]
        if not re.search(r"\b(?:not|no|never|cannot|can't|hasn't|haven't|wasn't)\b",prefix,re.I):
            errors.append('FALSE_TRANSACTION_CLAIM'); break
    ticket_ids=set(re.findall(r'MOCK-[a-z0-9]+',body,re.I))
    if ticket_ids and ticket_ids != ({ticket['ticket_id']} if ticket and ticket.get('status')=='created' else set()):
        errors.append('FALSE_TICKET_CLAIM')
    if ticket and ticket.get('status')=='created':
        if not re.search(r'\blocal mock\b|\bmock (?:ticket|handoff)\b',body,re.I):errors.append('G1_MOCK_SCOPE_REQUIRED')
        promise=r'\b(?:we|(?:our|the|a)\s+(?:(?:safety|support|policy|refunds?)\s+)?(?:team|agent|reviewer|specialist|team member))\s+(?:will|is going to)\s+(?:contact|reach|review|process|handle)\b|\b(?:wait|expect|look)\b.{0,18}\b(?:follow.up|response|contact|team)\b'
        if re.search(promise,body,re.I):errors.append('G1_REAL_HANDOFF_PROMISE')
    # All code facts may support dates/amounts, but policy text supports a number only
    # when its exact source is cited in this turn. This remains syntactic screening.
    support=[]
    for record in facts:
        if record['name']=='search_policy':
            for hit in record['data']['results']:
                ref={'source_id':'doc:'+hit['doc_id'],'section':hit['section_id'],'record_version':hit['version']}
                if json.dumps(ref,sort_keys=True) in cited: support.append(hit['text'])
        else: support.append(json.dumps(record['data']))
    source=' '.join(support)
    # A duration alone never establishes the event at which coverage begins.
    warranty_start=re.search(r'\bwarrant\w*\b.{0,100}\b(?:from|after|since|starting|begins?|starts?)\b.{0,30}\b(?:purchas\w*|deliver\w*|receipt|registration)\b',body,re.I)
    if warranty_start and not re.search(r'\b(?:from|after|since|starting|begins?|starts?)\b.{0,30}\b(?:purchas\w*|deliver\w*|receipt|registration)\b',source,re.I):
        # Explicitly unknown coverage starts do not assert a start event.
        clause=re.split(r'[.!?;]',body[:warranty_start.end()])[-1]
        if not re.search(r"not (?:specif|defin|establish)|unknown|cannot (?:confirm|determine)|does not (?:specif|defin|establish)",clause,re.I):
            errors.append('G3_UNSUPPORTED_WARRANTY_START')
    if any(f['name']=='get_tracking_events' and f['data'].get('stale') for f in facts):
        if not re.search(r'\bstale\b|\boutdated\b|\bnot current\b|\bnot (?:a )?live\b|\bmay have changed\b',body,re.I):
            errors.append('G3_STALE_TRACKING_DISCLOSURE')
    def normalize(value):
        # Grammar-only equivalence: 90-day and 90 days, never a unit conversion.
        value=re.sub(r'[-\s]+',' ',value.lower()).strip()
        return re.sub(r'\b(days|months)\b',lambda m:m.group(1)[:-1],value)
    for claim in POLICY_NUMBER.findall(body):
        if not re.search(r'(?<![\d.])'+re.escape(normalize(claim))+r'(?!\w|\.\d)',normalize(source)):
            # A numeric tool field is structured, so validate value/unit pairs explicitly.
            number=re.match(r'\$?(\d+(?:\.\d+)?)',claim).group(1)
            eligible=[r['data'] for r in facts if r['name']=='check_return_eligibility']
            supported=any((('day' in claim.lower() and float(number) in {d.get('window_days'),d.get('days_since_delivery')})
                or (claim.startswith('$') and float(number) in {d.get('refund_amount'),d.get('threshold')})) for d in eligible)
            if not supported: errors.append('G3_UNSUPPORTED_NUMBER'); break
    # A current shipping/tracking record is not a shipping-policy claim.
    policy_intents=any(re.search(r'policy|return|refund|warranty|cancel',intent,re.I) for intent in intents)
    if draft.outcome_claimed=='ANSWERED' and policy_intents and not any(r.source_id.startswith('doc:') for r in draft.citations):
        errors.append('G4_POLICY_CITATION_REQUIRED')
    # No policy numbers without citations even if an eligibility result quotes the rule.
    if POLICY_NUMBER.search(body) and not cited: errors.append('G4_EVIDENCE_REQUIRED')
    return sorted(set(errors))
