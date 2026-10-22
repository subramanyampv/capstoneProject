"""Check individualized eligibility assertions against scoped tool decisions.

This is bounded language screening, not unrestricted semantic entailment. Policy
conditions and explicit uncertainty are not individual eligibility decisions.
"""
from dataclasses import dataclass
import math
import re


@dataclass(frozen=True)
class EligibilityClaim:
    request_type: str | None
    decision: str


ASSERTION = re.compile(
    r"\byou\s+(?:(?:are|are not|aren't|aren’t|do not|don't|don’t)\s+)?(?:ineligible|eligible|qualify)\b|"
    r"\byou\s+(?:can|may|cannot|can't|can’t)\s+(?:return|cancel|receive\s+(?:a\s+)?refund|get\s+(?:a\s+)?refund)\b|"
    r"\byour\s+(?:(?:specific|individual)\s+)?(?:(?:return|refund|cancellation|order|item|request)\s+)?"
    r"(?:eligibility\s+(?:is|has been)\s+confirmed|(?:is|is not|isn't|isn’t)\s+(?:ineligible|eligible)|qualifies)\b",
    re.I)
UNCERTAIN = re.compile(
    r"\b(?:cannot|can't|can’t|unable to|could not|do not|don't|don’t)\s+"
    r"(?:yet\s+)?(?:confirm|verify|determine|establish|say|tell)\b|"
    r"\b(?:unknown|unverified|not confirmed|not verified)\b",re.I)


def eligibility_claims(body):
    # New sentences and contrast clauses close uncertainty/conditional scope.
    for clause in re.split(r'[.!?;\n]|\b(?:but|however|although)\b',body,flags=re.I):
        for match in ASSERTION.finditer(clause):
            prefix=clause[:match.start()]
            if UNCERTAIN.search(prefix) or re.search(r'\b(?:if|unless|whether)\b',prefix,re.I):
                continue
            if re.search(r'\b(?:if|provided that|as long as)\b',clause[match.end():],re.I):
                continue
            scope=clause[match.start():]
            kinds=set()
            if re.search(r'\brefund\b',scope,re.I):kinds.add('refund')
            if re.search(r'\breturns?\b',scope,re.I):kinds.add('return')
            if re.search(r'\bcancel\w*\b',scope,re.I):kinds.add('cancellation')
            negative=bool(re.search(r"\b(?:ineligible|not|aren't|aren’t|don't|don’t|cannot|can't|can’t)\b",match.group(),re.I))
            yield EligibilityClaim(next(iter(kinds)) if len(kinds)==1 else None,'ineligible' if negative else 'eligible')


def eligibility_errors(body,facts,*,order_id=None):
    errors=[]
    for claim in eligibility_claims(body):
        checks=[fact for fact in facts if fact['name']=='check_return_eligibility'
            and fact.get('args',{}).get('order_id') and fact.get('args',{}).get('sku')
            and (order_id is None or fact['args']['order_id']==order_id)
            and (claim.request_type is None or fact['args'].get('request_type')==claim.request_type)]
        # Ambiguous checks may not establish an unscoped individual entitlement.
        scopes={(fact['args']['order_id'],fact['args']['sku'],fact['args'].get('request_type')) for fact in checks}
        if not checks:
            errors.append('G3_UNVERIFIED_INDIVIDUAL_ELIGIBILITY')
        elif len(scopes)!=1 or any(fact['data'].get('decision')!=claim.decision for fact in checks):
            errors.append('G3_ELIGIBILITY_DECISION_MISMATCH')
    return sorted(set(errors))


@dataclass(frozen=True)
class AmountReviewClaim:
    """A bounded assertion that this refund needs amount-threshold review."""
    request_type: str = 'refund'


def amount_review_claims(body):
    # General conditional rules and human action alone are not causal claims.
    # Inspect bounded sentences rather than connecting unrelated policy statements.
    for clause in re.split(r'(?<!\d)\.|\.(?!\d)|[!?;\n]|\b(?:but|however|although)\b',body,flags=re.I):
        if not re.search(r'\bthreshold\b|\b(?:amount|refund)\b.{0,45}\b(?:exceeds?|above|over)\b',clause,re.I):
            continue
        requirement=re.search(r'\b(?:requires?|needs?|must|required)\b.{0,55}\b(?:human (?:review|action)|review)\b|'
                              r'\b(?:human (?:review|action)|review)\b.{0,30}\b(?:required|needed|mandatory)\b',clause,re.I)
        if not requirement:
            continue
        if UNCERTAIN.search(clause[:requirement.start()]):
            continue
        if re.search(r"\b(?:not|never|doesn't|does not|don't|do not)\b.{0,25}$",clause[:requirement.start()],re.I):
            continue
        if re.search(r"\b(?:review|action)\b.{0,15}\b(?:not|never|isn't|isn’t)\b.{0,12}\b(?:required|needed|mandatory)\b",clause,re.I):
            continue
        if re.search(r'\b(?:if|unless|whether|provided that)\b',clause,re.I):
            continue
        # Bind demonstratives to a transaction entity: "that threshold" and
        # "this assistant" describe general policy, not an individual refund.
        individual=re.search(
            r'\b(?:your|my)\s+(?:(?:specific|individual|requested)\s+)?(?:refund|request|amount|order)\b|'
            r'\b(?:this|that|the|our)\s+(?:(?:specific|individual|requested)\s+)?'
            r'(?:refund|request|amount|order)\b(?!\s+(?:amount\s+)?(?:threshold|limit|policy|rules?)\b)',
            clause,re.I)
        if not individual and re.search(r'\b(?:refunds|amounts)\b.{0,35}\b(?:above|over|exceed\w*)\b',clause,re.I):
            continue
        causal=re.search(r'\b(?:because|due to|per|under|based on)\b.{0,50}\b(?:threshold|amount)\b',clause,re.I)
        if individual or causal:
            yield AmountReviewClaim()


def amount_review_errors(body,facts,*,order_id=None):
    """Require one scoped refund decision and its actual amount-review reason.

    This is language screening, not unrestricted semantic entailment. A general
    human-action requirement remains valid even below the amount threshold.
    """
    if not any(amount_review_claims(body)):
        return []
    checks=[fact for fact in facts if fact.get('name')=='check_return_eligibility'
            and fact.get('args',{}).get('request_type')=='refund'
            and fact['args'].get('order_id') and fact['args'].get('sku')
            and (order_id is None or fact['args']['order_id']==order_id)]
    scopes={(f['args']['order_id'],f['args']['sku']) for f in checks}
    def supported(fact):
        data=fact.get('data',{});amount=data.get('refund_amount');threshold=data.get('threshold')
        numeric=lambda value:isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value)
        return (data.get('decision')=='requires_review'
                and 'REFUND_ABOVE_THRESHOLD' in data.get('reason_codes',[])
                and numeric(amount) and numeric(threshold) and amount>threshold)
    if len(scopes)!=1 or not checks or not all(supported(fact) for fact in checks):
        return ['G3_UNSUPPORTED_AMOUNT_REVIEW_CAUSE']
    return []
