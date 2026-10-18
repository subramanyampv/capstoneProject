"""Turn-local request obligations, independent of planner/specialist declarations.

The bounded lexical parser is deliberately inspectable. It adds requirements for
recognized support requests; it is not a claim of unrestricted language understanding.
"""
from dataclasses import dataclass, asdict
import json
import re

VERSION = 'request-obligations-v2'
ORDER = re.compile(r'\bO-\d{4}\b', re.I)
RETURN = re.compile(r'\b(?:returns?|returning|retrun|restocking)\b|\bsend\b.{0,25}\bback\b', re.I)
REFUND = re.compile(r'\brefund\w*\b', re.I)
# A monetary reimbursement remains a refund obligation even when the customer
# never uses the word "refund". Item-return wording alone is not enough.
REIMBURSEMENT = re.compile(
    r'\breimburs\w*\b|\b(?:my |the )?money\s+back\b|'
    r'\b(?:pay|credit)\s+(?:me\s+)?back\b|'
    r'\b(?:send|give|pay|credit|return)\s+(?:me\s+)?(?:back\s+)?'
    r'(?:(?:the|my|entire|full|whole|all|of|amount|sum|payment)\s+){0,5}'
    r'(?:[$€£]\s*\d[\d,.]*|\d[\d,.]*\s*(?:dollars?|USD|EUR|GBP)\b)'
    r'(?=\s*(?:[.!?;]|$|\b(?:for|to|back|and|on)\b))', re.I)
CANCEL = re.compile(r'\bcancel\w*\b', re.I)
WITHDRAW_CANCELLATION = re.compile(r"\b(?:do not|don't|don’t)\s+cancel\b|\bkeep\s+(?:my|the|this|that)\s+order\b|\bstop\b.{0,20}\bcancellation\b",re.I)
TRACK = re.compile(r'\btrack\w*\b|latest.{0,20}event|\bwhere.{0,35}\b(?:order|package)\b|\bwhen.{0,35}\b(?:ship|arriv|deliver)', re.I)
RECENT_TRACKING = re.compile(r'\b(?:latest|most recent|last)\b.{0,30}\b(?:carrier|scan|event|tracking)\b|\bcarrier\s+(?:scan|update)\b', re.I)
DELIVERY_SUBJECT = re.compile(r'\b(?:arriv\w*|deliver\w*|reach)\b|\bget here\b', re.I)
DELIVERY_FUTURE = re.compile(r'\b(?:when|will|tomorrow|today|certain\w*|guarantee\w*|promis\w*|predict\w*|estimat\w*)\b', re.I)
STATUS = re.compile(r'\b(?:order|package).{0,20}\bstatus\b|\b(?:has|did|hadn.t|hasn.t|it|not|never).{0,30}\bship\w*\b|\bdelivery email\b', re.I)
PRODUCT = re.compile(r'material|\bsize\b|sizing|\bcare\b|\bwash\w*\b|\bclean\w*\b|weight|specification|\bwarrant\w*\b|opened', re.I)
SHIPPING = re.compile(r'\bshipping\b|\bship\b.{0,35}\b(?:canada|international|usually|standard)\b|\barrive\b|\bdelivery estimate\b', re.I)
GENERAL = re.compile(r'\bpolicy|\brule\b|\bwindow|\bdeadline|\blargest|\bthreshold|how many|\bdocument|\bfee|\bguarantee|how long|\bfaq\b|\bhelp (?:page|center|centre)\b', re.I)

@dataclass(frozen=True)
class Obligations:
    intents: tuple[str, ...]
    order_id: str | None
    request_types: tuple[str, ...]
    policy_docs: tuple[str, ...]
    tracking: bool = False
    order_status: bool = False
    product: bool = False
    ambiguous_orders: bool = False
    sku: str | None = None
    needs_reference: bool = False
    required_sections: tuple[str, ...] = ()
    version: str = VERSION

    def public(self):
        return asdict(self)

    def public_policy_question(self):
        """Resolved public policy scope does not require a private order."""
        return bool(self.policy_docs and not
                    (self.order_id or self.needs_reference or self.ambiguous_orders))

    def agents(self):
        names=[]
        if self.order_id and (self.tracking or self.order_status or self.request_types or self.product):names.append('order_shipping')
        if self.policy_docs or self.request_types or self.product:names.append('policy_product')
        return names


def derive(query, context=None, *, services=None):
    context=context or {}
    ids=list(dict.fromkeys(value.upper() for value in ORDER.findall(query)))
    resolved=ids[0] if len(ids)==1 else context.get('resolved_order_id') if not ids else None
    if not resolved and not ids and STATUS.search(query):resolved=context.get('entities',{}).get('order_id')
    tracking=bool(TRACK.search(query) or RECENT_TRACKING.search(query));status=bool(STATUS.search(query))
    delivery_future=bool(DELIVERY_SUBJECT.search(query) and DELIVERY_FUTURE.search(query))
    if re.search(r'what.{0,25}mean.{0,20}\b(?:my|the|that) order\b',query,re.I):
        status=True
        tracking=bool(set(context.get('last_intents',[])) & {'order_tracking','shipping_tracking'})
    # Named return/refund discussions may include a historic delivery date without
    # asking a new tracking question. Only explicit tracking wording creates it.
    has_return=bool(RETURN.search(query));has_refund=bool(REFUND.search(query) or REIMBURSEMENT.search(query));withdraw=bool(WITHDRAW_CANCELLATION.search(query))
    has_cancel=bool(CANCEL.search(query)) and not withdraw
    individual=re.search(r'\b(?:can I|can you|I want|I need)\s+(?:please\s+)?(?:return|refund|cancel|start|request)\b|\b(?:start|approve|cancel)\s+(?:my|this|that|order|O-)',query,re.I)
    general=bool(GENERAL.search(query)) and not individual
    refund_status=has_refund and bool(re.search(r'refund.{0,25}(?:approved yet|arriv|status|processed)',query,re.I))
    requests=[];docs=[];intents=[]
    if tracking or status:intents.append('order_tracking')
    if withdraw:intents.append('cancellation')
    if re.search(r'\b(?:shorter|too verbose|too long|more detail)\b',query,re.I):intents.append('feedback_style')
    for flag,kind,doc,intent in [(has_cancel,'cancellation','cancellation_policy','cancellation'),
                                (has_refund,'refund','refund_policy','refund_request'),
                                (has_return,'return','return_policy','return_eligibility')]:
        if flag:
            intents.append('refund_status' if refund_status and kind=='refund' else intent)
            if not refund_status:docs.append(doc)
            if resolved and not general and not refund_status:requests.append(kind)
    product=bool(PRODUCT.search(query))
    if product:intents.append('warranty' if re.search(r'warrant',query,re.I) else 'product_information')
    if re.search(r'warrant',query,re.I):docs.append('warranty_policy')
    if delivery_future or (SHIPPING.search(query) and (not resolved or re.search(r'estimat|arriv|guarantee|usually|standard',query,re.I))):
        docs.append('shipping_policy');intents.append('policy_question')
    if refund_status:status=True
    if has_refund and re.search(r'window|deadline|footwear',query,re.I):docs.append('return_policy')
    if has_return and re.search(r'\bfaq\b|\bhelp (?:page|center|centre)\b',query,re.I):docs.append('faq')
    product_ref=catalog_reference(query,services,context) if services else None
    # A public, conditional product-policy question does not require a private
    # order. An individual eligibility request does, even when retrieval succeeds.
    conditional=bool(product_ref and re.search(r'\bif\b',query,re.I))
    unknown_policy_subject=has_return and bool(re.search(r'policy\s+for\b',query,re.I)) and not product_ref and not re.search(r'footwear|apparel|home|electronics|perishable|grocery',query,re.I)
    needs_reference=not resolved and not conditional and bool(
        ((has_return or has_refund or has_cancel or tracking or status) and not general)
        or unknown_policy_subject
        or (not intents and re.search(r'\b(?:again|previous answer|earlier question)\b',query,re.I)))
    sections=('return_policy:restocking',) if re.search(r'restock',query,re.I) else ()
    return Obligations(tuple(dict.fromkeys(intents)),resolved,tuple(requests),tuple(dict.fromkeys(docs)),
        tracking,status,product,len(ids)>1,product_ref.get('sku') if product_ref else None,
        needs_reference,sections)


def catalog_reference(query, services, context=None):
    """Public catalog names select a tool argument, never supply answer facts."""
    catalog=services.read('product_catalog.json')['products']
    explicit=re.findall(r'\bSKU-[A-Z0-9-]+\b',query,re.I)
    if len(set(explicit))==1:return {'sku':explicit[0].upper()}
    matches=[]
    for item in catalog:
        terms=[word for word in re.findall(r'[A-Za-z]+',item['name']) if len(word)>=4 and word.lower() not in {'gourmet'}]
        if any(re.search(r'\b'+re.escape(word.rstrip('s'))+r's?\b',query,re.I) for word in terms):matches.append(item)
    if len(matches)==1:return {'sku':matches[0]['sku']}
    context=context or {}
    if not matches and context.get('resolved_sku'):return {'sku':context['resolved_sku']}
    return None


def normalize_plan(parsed, contract):
    """Planner may enrich tasks; it cannot remove recognized request obligations."""
    data=parsed.model_dump()
    if contract.ambiguous_orders:
        data.update(steps=[],clarification='Please choose one order at a time so each request can be verified.',order_id=None)
        return data
    if contract.order_id:data['order_id']=contract.order_id
    required=contract.agents()
    steps={step['agent']:step for step in data['steps']}
    names=list(dict.fromkeys([*required,*[step['agent'] for step in data['steps']]]))
    names.sort(key=lambda name:{'order_shipping':0,'policy_product':1,'escalation':2}[name])
    rebuilt=[]
    for name in names:
        step=steps.get(name,{'agent':name,'task':'Fulfill the independent request obligations using verified current-turn tools.','depends_on':[]})
        deps=[0] if name=='policy_product' and rebuilt and rebuilt[0]['agent']=='order_shipping' else []
        rebuilt.append({**step,'depends_on':deps})
    data['steps']=rebuilt
    data['intents']=list(dict.fromkeys([*contract.intents,*data['intents']]))[:8]
    if contract.needs_reference:
        data['clarification']='Please provide a valid order reference or clarify the product and request so I can verify it.'
    elif contract.order_id or contract.public_policy_question():data['clarification']=None
    return data


def matching_fact(facts,name,**args):
    return next((fact for fact in facts if fact['name']==name and all(fact['args'].get(key)==value for key,value in args.items())),None)


async def fulfill(contract,agent,registry,query,context=None):
    """Backfill only missing reads through the same authorized, bounded registry."""
    ctx=registry.ctx
    async def attempt(name,args):
        # Never retry the same failed read implicitly or spend the handoff slot.
        if any(f['name']==name and all(f['args'].get(k)==v for k,v in args.items()) for f in ctx.facts):return
        if any(row['name']==name and row['status']=='error' and row['error'] in
               {'NOT_FOUND','TIMEOUT','FAILED','INDEX_UNAVAILABLE','BUDGET_EXCEEDED'} for row in ctx.records):return
        await registry.call(agent,name,args)
    if contract.ambiguous_orders:return
    if agent=='order_shipping' and contract.order_id:
        if contract.request_types or contract.product or contract.order_status or contract.tracking:
            await attempt('lookup_order',{'order_id':contract.order_id})
        if contract.tracking and matching_fact(ctx.facts,'lookup_order',order_id=contract.order_id):
            await attempt('get_tracking_events',{'order_id':contract.order_id})
    if agent!='policy_product':return
    owned=matching_fact(ctx.facts,'lookup_order',order_id=contract.order_id) if contract.order_id else None
    product_args=None
    if owned and len(owned['data']['items'])==1:product_args={'sku':owned['data']['items'][0]['sku']}
    elif not contract.order_id:product_args=catalog_reference(query,registry.services,context)
    if (contract.product or (not owned and contract.policy_docs and contract.sku)) and product_args:await attempt('get_product_details',product_args)
    for kind in contract.request_types:
        if owned and len(owned['data']['items'])==1:
            await attempt('check_return_eligibility',{'order_id':contract.order_id,'sku':owned['data']['items'][0]['sku'],'request_type':kind})
    required_docs=set(contract.policy_docs)
    for fact in ctx.facts:
        if fact['name']=='check_return_eligibility':required_docs.update(ref['source_id'][4:] for ref in fact['data']['policy_refs'])
    hits=[hit for fact in ctx.facts if fact['name']=='search_policy' for hit in fact['data']['results']]
    missing=required_docs-{hit['doc_id'] for hit in hits if hit['authority']=='policy' or
                           (hit['doc_id']=='faq' and hit['authority']=='faq')}
    for fact in ctx.facts:
        if fact['name']=='check_return_eligibility':
            for ref in fact['data']['policy_refs']:
                if not any(hit['doc_id']==ref['source_id'][4:] and hit['section_id']==ref['section'] and hit['version']==ref['record_version'] for hit in hits):
                    missing.add(ref['source_id'][4:])
    for section in contract.required_sections:
        doc,heading=section.split(':',1)
        if not any(hit['doc_id']==doc and hit['section_id']==heading and hit['authority']=='policy' for hit in hits):missing.add(doc)
    if missing:
        hints={'return_policy':'return policy calendar days window condition exclusions restocking exceptions',
               'refund_policy':'refund policy request review threshold delayed shipments',
               'cancellation_policy':'cancellation policy eligibility before dispatch human action',
               'shipping_policy':'shipping policy estimates standard international guaranteed',
               'warranty_policy':'warranty policy product category duration coverage',
               'faq':'FAQ return policy source comparison'}
        # Preserve bounded public topic hints without copying arbitrary customer
        # text/identifiers into tool arguments. Hints never establish category authority.
        topics=[word for word in ['electronics','footwear','apparel','home','perishable','grocery','speaker','jacket','shoes','pots']
                if re.search(r'\b'+word+r'\b',query,re.I)]
        text=' '.join(hints[doc] for doc in sorted(missing))+' '+' '.join(topics)
        if 'return_policy:restocking' in contract.required_sections:text='opened electronics restocking fee'
        category=next(iter(ctx.categories)) if len(ctx.categories)==1 else None
        await attempt('search_policy',{'query':text,'doc_types':sorted(missing),'category':category,'k':10})


def audit(contract,facts):
    """Record evidence coverage without trusting plan or claimed intent labels."""
    rows=[]
    def add(kind,complete,needed):rows.append({'obligation':kind,'evidence_complete':bool(complete),'required':needed})
    if contract.needs_reference:add('request_reference',False,['valid_order_or_product_reference'])
    if contract.tracking:add('order_tracking',matching_fact(facts,'get_tracking_events',order_id=contract.order_id),['get_tracking_events'])
    elif contract.order_status:add('order_tracking',matching_fact(facts,'lookup_order',order_id=contract.order_id),['lookup_order'])
    for kind in contract.request_types:
        add(kind,matching_fact(facts,'check_return_eligibility',order_id=contract.order_id,request_type=kind),['check_return_eligibility:'+kind])
    if contract.product:
        owned=matching_fact(facts,'lookup_order',order_id=contract.order_id)
        sku=contract.sku or (owned['data']['items'][0]['sku'] if owned and len(owned['data']['items'])==1 else None)
        add('product_information',sku and matching_fact(facts,'get_product_details',sku=sku),['get_product_details:requested_product'])
    if 'refund_status' in contract.intents:add('refund_status',False,['refund_state_not_available_in_tool_contract'])
    hits=[hit for fact in facts if fact['name']=='search_policy' for hit in fact['data']['results']]
    required=set(contract.policy_docs)
    for fact in facts:
        if fact['name']=='check_return_eligibility':required.update(ref['source_id'][4:] for ref in fact['data']['policy_refs'])
    for doc in sorted(required):add('policy:'+doc,any(hit['doc_id']==doc and
        (hit['authority']=='policy' or (doc=='faq' and hit['authority']=='faq')) for hit in hits),['search_policy:'+doc])
    for section in contract.required_sections:
        doc,heading=section.split(':',1)
        add('section:'+section,any(hit['doc_id']==doc and hit['section_id']==heading and hit['authority']=='policy' for hit in hits),['search_policy:requested_section'])
    for fact in facts:
        if fact['name']=='check_return_eligibility':
            for ref in fact['data']['policy_refs']:
                add('rule:'+ref['source_id']+':'+ref['section'],any(hit['doc_id']==ref['source_id'][4:] and hit['section_id']==ref['section'] and hit['version']==ref['record_version'] for hit in hits),['search_policy:exact_rule_reference'])
    return rows


def citation_errors(contract,facts,draft):
    citations={ref.source_id for ref in draft.citations}
    required={row['obligation'][7:] for row in audit(contract,facts) if row['obligation'].startswith('policy:') and row['evidence_complete']}
    errors=['O2_AUTHORITATIVE_CITATION:'+doc for doc in sorted(required) if 'doc:'+doc not in citations]
    cited={json.dumps(ref.model_dump(),sort_keys=True) for ref in draft.citations}
    hits=[hit for fact in facts if fact['name']=='search_policy' for hit in fact['data']['results']]
    for section in contract.required_sections:
        doc,heading=section.split(':',1)
        matching=[hit for hit in hits if hit['doc_id']==doc and hit['section_id']==heading and hit['authority']=='policy']
        if matching and not any(ref.source_id=='doc:'+doc and ref.section==heading and any(ref.record_version==hit['version'] for hit in matching) for ref in draft.citations):errors.append('O2_SECTION_CITATION:'+section)
    for fact in facts:
        if fact['name']=='check_return_eligibility':
            for ref in fact['data']['policy_refs']:
                if any(hit['doc_id']==ref['source_id'][4:] and hit['section_id']==ref['section'] and hit['version']==ref['record_version'] for hit in hits) and json.dumps(ref,sort_keys=True) not in cited:
                    errors.append('O2_RULE_CITATION:'+ref['source_id']+':'+ref['section'])
    return sorted(set(errors))
