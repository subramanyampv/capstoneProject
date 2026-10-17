"""Read-only synthetic domain services and the sole permitted mock write."""
import hashlib
import json
import sqlite3
import threading
import uuid
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path
from capstone_agent.support.contracts import *
from capstone_agent.support.privacy import minimize, opaque

ROOT = Path(__file__).resolve().parents[3]
SCENARIO_DATE = date(2026,10,12)

class ToolFailure(Exception):
    def __init__(self, code, details=None):
        self.code, self.details = code, details

class Services:
    def __init__(self, *, root=ROOT, search=None, ticket_path=None):
        self.root, self.search = root, search
        self.ticket_path = ticket_path or root/'data/runtime/tickets.sqlite3'
        self.lock = threading.Lock()
        self.rules = self.read('policy_rules.json')
        # Detect document/config drift before serving deterministic policy decisions.
        from capstone_agent.retrieval.corpus import load_corpus, check_rule_consistency
        chunks, _, quarantine = load_corpus(root/'knowledge/raw')
        if quarantine:
            raise ValueError('CORPUS_QUARANTINED')
        check_rule_consistency(chunks, self.rules)
        self.policy_refs = { (c['metadata']['doc_id'],c['metadata']['section_id']):
            EvidenceRef(source_id='doc:'+c['metadata']['doc_id'], section=c['metadata']['section_id'],
                        record_version=c['metadata']['version']).model_dump() for c in chunks }

    def read(self, name):
        return json.loads((self.root/'data'/name).read_text())

    def customers(self):
        return sorted({o['customer_ref'] for o in self.read('sample_orders.json')['orders']})

    def owned(self, order_id, customer):
        raw = self.read('sample_orders.json')
        order = next((o for o in raw['orders'] if o['order_id']==order_id and o['customer_ref']==customer),None)
        if order is None:
            raise ToolFailure('NOT_FOUND')
        return order, raw['version']

    def lookup_order(self, args, ctx):
        order, version = self.owned(args.order_id, ctx.customer_id)
        return OrderResult(order_id=order['order_id'], status=order['status'], placed_at=order['placed_on'],
            dispatched_at=order['shipped_on'], delivered_at=order['delivered_on'],
            items=[OrderItem(sku=order['item_sku'],name=order['item_name'],category=order['category'],price=float(order['amount_usd']))],
            record_version=version)

    def get_tracking_events(self, args, ctx):
        order,_ = self.owned(args.order_id, ctx.customer_id)
        raw=self.read('sample_tracking_events.json')
        events=sorted(raw['events'].get(args.order_id,[]),key=lambda e:datetime.fromisoformat(e['timestamp'].replace('Z','+00:00')))
        events=[e for e in events if date.fromisoformat(e['timestamp'][:10])<=ctx.today]
        estimate=events[-1].get('carrier_estimate') if events else None
        if estimate is not None:
            try: date.fromisoformat(estimate)
            except (ValueError,TypeError): raise ToolFailure('MISSING_DATA') from None
        events=[TrackingEvent(ts=e['timestamp'],status=e['event'],city=e['location']) for e in events]
        latest=events[-1] if events else None
        gap=(ctx.today-date.fromisoformat(latest.ts[:10])).days if latest else None
        # A completed delivery does not become a stale in-transit shipment.
        stale=order['status']!='delivered' and (gap is None or gap>=5)
        return TrackingResult(events=events,latest=latest,stale=stale,carrier_estimate=estimate,record_version=raw['version'])

    def get_product_details(self,args,ctx):
        raw=self.read('product_catalog.json'); products=raw['products']
        if args.sku:
            found=[p for p in products if p['sku']==args.sku and (not args.name or args.name.casefold() in p['name'].casefold())]
        else:
            found=[p for p in products if args.name.strip().casefold() in p['name'].casefold()]
        if not found: raise ToolFailure('NOT_FOUND')
        if len(found)>1: raise ToolFailure('AMBIGUOUS',{'candidates':[{'sku':p['sku'],'name':p['name']} for p in found]})
        p=found[0]
        return ProductResult(sku=p['sku'],name=p['name'],category=p['category'],return_category=p['category'],
            warranty_days=self.rules['warranty_days'][p['category']],
            specs={k:p.get(k) for k in ['material','sizes','care','sizing_note']},record_version=raw['version'])

    def search_policy(self,args,ctx):
        if self.search is None: raise ToolFailure('INDEX_UNAVAILABLE')
        # A restrictive category must be resolved this turn from a verified product/order,
        # not chosen by the model merely to suppress contradictory evidence.
        if args.category and args.category not in ctx.categories:
            raise ToolFailure('UNVERIFIED_CATEGORY')
        try:
            result=self.search.search(args.query,doc_types=args.doc_types,category=args.category,k=args.k,today=ctx.today)
        except ValueError as exc:
            code=str(exc)
            raise ToolFailure(code if code in {'INDEX_UNAVAILABLE','MANIFEST_MISMATCH','INVALID_ARGUMENT','TOO_MANY_CONFLICTING_SOURCES'} else 'RETRIEVAL_FAILED') from None
        fields=PolicyHit.model_fields
        return PolicyResult(results=[PolicyHit(**{k:v for k,v in row.items() if k in fields}) for row in result['results']],
            below_threshold=result['below_threshold'],conflict=result['conflict'],conflict_details=result['conflict_details'],
            index_version=result['index_version'],category_filter=result['category_filter'],
            conflict_evidence_exceeds_k=result['conflict_evidence_exceeds_k'])

    def check_return_eligibility(self,args,ctx):
        order,_=self.owned(args.order_id,ctx.customer_id)
        if args.sku!=order['item_sku']: raise ToolFailure('NOT_FOUND')
        r=self.rules; category=order['category']; decision='unknown'; reasons=[]; days=None; window=None
        threshold=float(r['refund_auto_approve_max_amount'])
        amount=float(Decimal(str(order['amount_usd'])))
        doc='cancellation_policy' if args.request_type=='cancellation' else 'return_policy'
        section='eligibility' if args.request_type=='cancellation' else 'window'
        refs=[self.policy_refs[(doc,section)]]
        if args.request_type=='cancellation':
            allowed=order['status'] in r['cancellation_allowed_statuses'] and not order['shipped_on']
            decision='eligible' if allowed else 'ineligible'
            reasons=['CANCELLATION_PRE_DISPATCH' if allowed else 'ALREADY_DISPATCHED']
        elif category in r['return_excluded_categories']:
            decision='ineligible'; reasons=['CATEGORY_EXCLUDED']; refs=[self.policy_refs[('return_policy','exclusions')]]
        elif order['status']!='delivered':
            decision='unknown'; reasons=['NOT_DELIVERED']
        elif not order['delivered_on']:
            reasons=['MISSING_DELIVERY_DATE']
        else:
            try: days=(ctx.today-date.fromisoformat(order['delivered_on'])).days
            except ValueError: raise ToolFailure('MISSING_DATA') from None
            if days<0: reasons=['INVALID_DELIVERY_DATE']
            else:
                window=r['return_window_days'].get(category,r['return_window_days']['default'])
                within=days<=window if r['return_window_inclusive'] else days<window
                decision='eligible' if within else 'ineligible'
                reasons=['WITHIN_WINDOW' if within else 'WINDOW_EXCEEDED']
        if args.request_type=='refund':
            refs.append(self.policy_refs[('refund_policy','review-threshold')])
            if amount>threshold:
                decision='requires_review'; reasons.append('REFUND_ABOVE_THRESHOLD')
        return EligibilityResult(decision=decision,reason_codes=reasons,window_days=window,days_since_delivery=days,
            refund_amount=amount if args.request_type=='refund' else None,threshold=threshold,rule_version=r['version'],
            policy_refs=refs,human_action_required=decision in {'eligible','requires_review'})

    def create_escalation(self,args,ctx):
        if minimize(args.summary,ctx.secrets)!=args.summary:
            raise ToolFailure('PII_REJECTED')
        if any(json.dumps(ref.model_dump(),sort_keys=True) not in ctx.evidence for ref in args.evidence_refs):
            raise ToolFailure('UNRESOLVED_EVIDENCE')
        if args.order_ref:
            self.owned(args.order_ref,ctx.customer_id)
        if not set(args.triggers) <= ctx.triggers:
            raise ToolFailure('UNVERIFIED_TRIGGER')
        triggers=sorted(ctx.triggers)
        # Selection comes from code-bound flags, never model-supplied queue/priority.
        queue='safety' if 'T1' in triggers else 'legal' if ctx.legal and 'T6' in triggers else next(
            (q for t,q in [('T2','refunds'),('T3','policy'),('T4','returns_exceptions')] if t in triggers),'general')
        priority='high' if queue in {'safety','legal'} else 'normal'
        reference=opaque(args.order_ref) if args.order_ref else None
        identity=json.dumps([ctx.session_id,ctx.customer_id,triggers,reference,queue,priority],sort_keys=True)
        key=hashlib.sha256(identity.encode()).hexdigest()
        # Persist only generated reasons; free-form names cannot evade pattern masking.
        stored_summary='Human review requested. Verified reason codes: '+', '.join(triggers)+'.'
        packet={'triggers':triggers,'summary':stored_summary,'evidence_refs':[
            {**ref.model_dump(),'source_id':minimize(ref.source_id)} for ref in args.evidence_refs],
            'order_ref':reference,'customer_ref':opaque(ctx.customer_id),'queue':queue,'priority':priority}
        with self.lock:
            self.ticket_path.parent.mkdir(parents=True,exist_ok=True)
            with sqlite3.connect(self.ticket_path,timeout=1) as db:
                db.execute('CREATE TABLE IF NOT EXISTS tickets (key TEXT PRIMARY KEY, payload TEXT NOT NULL)')
                saved=db.execute('SELECT payload FROM tickets WHERE key=?',(key,)).fetchone()
                replay=saved is not None
                if not saved:
                    result={'ticket_id':'MOCK-'+uuid.uuid4().hex[:12],'status':'created','queue':queue,'priority':priority,
                        'triggers':triggers,'summary_hash':hashlib.sha256(stored_summary.encode()).hexdigest(),'idempotent_replay':False}
                    db.execute('INSERT INTO tickets VALUES (?,?)',(key,json.dumps({'result':result,'packet':packet})))
                    db.commit()
                saved=db.execute('SELECT payload FROM tickets WHERE key=?',(key,)).fetchone()
                if not saved: raise ToolFailure('FAILED')
                result=json.loads(saved[0])['result']
                result['idempotent_replay']=replay
        # Read-back above is required before returning a success claim.
        return EscalationResult(**result)
