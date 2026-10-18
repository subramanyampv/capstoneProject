"""Per-turn permissions, closed schemas, deadlines, budgets and LangChain tools."""
import asyncio
import json
import time
import uuid
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from pydantic import ValidationError
from langchain_core.tools import StructuredTool
from capstone_agent.support.contracts import *
from capstone_agent.support.services import Services, ToolFailure, SCENARIO_DATE

@dataclass(frozen=True)
class SessionIdentity:
    customer_id: str
    session_id: str = field(default_factory=lambda: uuid.uuid4().hex)

@dataclass
class ToolContext:
    identity: SessionIdentity
    today: date = SCENARIO_DATE
    secrets: tuple[str,...] = ()
    calls: int = 0
    allowed_order_ids: set[str] | None = None
    refund_order_ids: set[str] = field(default_factory=set)
    triggers: set[str] = field(default_factory=set)
    legal: bool = False
    categories: set[str] = field(default_factory=set)
    evidence: set[str] = field(default_factory=set)
    records: list[dict] = field(default_factory=list)
    facts: list[dict] = field(default_factory=list)
    faults: dict[str,str] = field(default_factory=dict)
    @property
    def customer_id(self): return self.identity.customer_id
    @property
    def session_id(self): return self.identity.session_id

# domain methods have no LangChain dependency. This adapter owns schemas/permissions.
SPECS={
 'lookup_order':('order_shipping',OrderArgs,OrderResult,3.),
 'get_tracking_events':('order_shipping',OrderArgs,TrackingResult,3.),
 # User-approved 20-second local retrieval budget. Latency is measured
 # separately from correctness; results after the deadline cannot become evidence.
 'search_policy':('policy_product',PolicyArgs,PolicyResult,20.),
 'get_product_details':('policy_product',ProductArgs,ProductResult,2.),
 'check_return_eligibility':('policy_product',EligibilityArgs,EligibilityResult,2.),
 'create_escalation':('escalation',EscalationArgs,EscalationResult,3.),
}
DESCRIPTIONS={
 'lookup_order':'Read an owned order by O-1234 identifier; identity is supplied by the server.',
 'get_tracking_events':'Read owned tracking events; disclose missing carrier estimates and stale in-transit data.',
 'search_policy':'Retrieve current policy evidence. doc_types accepts only return_policy, refund_policy, shipping_policy, cancellation_policy, warranty_policy, faq, escalation_guidelines; omit it to search all. Values such as policy or return are invalid. Omit category unless verified this turn by a product/order tool. Never choose between conflicting sources.',
 'get_product_details':'Find catalog facts using SKU or product-name substring; missing specifications stay unknown.',
 'check_return_eligibility':'Compute information-only return/refund/cancellation eligibility from owned records; does not execute transactions.',
 'create_escalation':'Create and verify a sanitized local mock handoff. Queue/priority come from server triggers. No promises or personal data.',
}

class Registry:
    def __init__(self, services: Services, ctx: ToolContext):
        if ctx.customer_id not in services.customers(): raise ValueError('UNKNOWN_SYNTHETIC_CUSTOMER')
        self.services,self.ctx=services,ctx

    def tools(self, agent):
        def build(name,schema):
            async def invoke(**kwargs):
                return (await self.call(agent,name,kwargs)).model_dump()
            return StructuredTool.from_function(coroutine=invoke,name=name,description=DESCRIPTIONS[name],args_schema=schema)
        return [build(name,schema) for name,(owner,schema,_,_) in SPECS.items() if owner==agent]

    def remember(self,name,data,args):
        self.ctx.facts.append({'name':name,'args':args,'data':data})
        refs=[]
        if name=='lookup_order':
            if data['order_id'] in self.ctx.refund_order_ids:
                amount=sum(Decimal(str(item['price'])) for item in data['items'])
                if amount>Decimal(str(self.services.rules['refund_auto_approve_max_amount'])):self.ctx.triggers.add('T2')
            self.ctx.categories.update(item['category'] for item in data['items'])
            refs=[EvidenceRef(source_id='order:'+data['order_id'],record_version=data['record_version']).model_dump()]
        elif name=='get_tracking_events':
            refs=[EvidenceRef(source_id='tracking:'+args['order_id'],record_version=data['record_version']).model_dump()]
        elif name=='get_product_details':
            self.ctx.categories.add(data['category'])
            refs=[EvidenceRef(source_id='product:'+data['sku'],record_version=data['record_version']).model_dump()]
        elif name=='check_return_eligibility':
            refs=data['policy_refs']
            if data['decision']=='requires_review': self.ctx.triggers.add('T2')
            if args['request_type']=='cancellation' and data['decision']=='eligible': self.ctx.triggers.add('T6')
        elif name=='search_policy':
            refs=[EvidenceRef(source_id='doc:'+r['doc_id'],section=r['section_id'],record_version=r['version']).model_dump() for r in data['results']]
            if data['conflict']: self.ctx.triggers.add('T3')
        self.ctx.evidence.update(json.dumps(ref,sort_keys=True) for ref in refs)
        return refs

    async def call(self,agent,name,arguments):
        from capstone_agent.observability.support_tracing import span
        with span(name,'tool') as output:
            result=await self._call(agent,name,arguments)
            output['failed']=result.status=='error'
            return result

    async def _call(self,agent,name,arguments):
        started=time.perf_counter(); exec_id=uuid.uuid4().hex
        result=None; code=None; data=None; refs=[]
        try:
            # Count attempts, including malformed args, and reserve the eighth slot for handoff.
            if self.ctx.calls>=8 or (self.ctx.calls>=7 and not (name=='create_escalation' and agent=='escalation')):
                self.ctx.triggers.add('T5'); raise ToolFailure('BUDGET_EXCEEDED')
            self.ctx.calls+=1
            if name not in SPECS: raise ToolFailure('UNKNOWN_TOOL')
            owner,inputs,outputs,timeout=SPECS[name]
            if agent!=owner: raise ToolFailure('PERMISSION_DENIED')
            if not isinstance(arguments,dict): raise ToolFailure('INVALID_ARGUMENT')
            arguments={k:v for k,v in arguments.items() if k not in {'customer_id','customer_ref','session_id'}}
            args=inputs.model_validate(arguments)
            if name in {'lookup_order','get_tracking_events','check_return_eligibility'} and self.ctx.allowed_order_ids is not None and args.order_id not in self.ctx.allowed_order_ids:
                raise ToolFailure('UNEXPECTED_ORDER')
            fault=self.ctx.faults.get(name)
            if fault: raise ToolFailure(fault)
            method=getattr(self.services,name)
            if name=='create_escalation':
                # Controlled local write commits/read-backs synchronously. Never abandon a
                # write worker on timeout and later create an unreported orphan ticket.
                result=method(args,self.ctx)
            else:
                result=await asyncio.wait_for(asyncio.to_thread(method,args,self.ctx),timeout)
            data=outputs.model_validate(result).model_dump()
            refs=self.remember(name,data,args.model_dump())
        except ToolFailure as exc:
            code=exc.code
            if exc.details: data=exc.details
        except ValidationError as exc:
            code='INVALID_ARGUMENT'
            fields=SPECS[name][1].model_fields if name in SPECS else {}
            labels=[]
            for error in exc.errors(include_input=False,include_url=False):
                field=str(error['loc'][0]) if error['loc'] and error['loc'][0] in fields else 'arguments'
                labels.append(error['type']+'@'+field)
            data={'argument_errors':sorted(set(labels))[:8],'retry_with_exact_tool_schema':True}
        except TypeError: code='INVALID_ARGUMENT'
        except TimeoutError: code='TIMEOUT'
        except Exception: code='FAILED'  # never stringify provider/storage exceptions
        record=ToolResult(evidence_refs=refs,exec_id=exec_id,name=name,status='error' if code else 'ok',data=data,error=code,
                          duration_ms=round((time.perf_counter()-started)*1000,3))
        self.ctx.records.append(record.model_dump())
        return record
