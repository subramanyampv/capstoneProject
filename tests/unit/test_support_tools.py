"""Authorization, deterministic rules, verified writes and bounded registry behavior."""
import asyncio
import json
import shutil
from datetime import date
from pathlib import Path
import pytest
from capstone_agent.support.registry import Registry,ToolContext,SessionIdentity
from capstone_agent.support.services import Services,ROOT

@pytest.fixture
def setup(tmp_path):
    shutil.copytree(ROOT/'data',tmp_path/'data',ignore=shutil.ignore_patterns('runtime'))
    shutil.copytree(ROOT/'knowledge/raw',tmp_path/'knowledge/raw')
    services=Services(root=tmp_path)
    def make(customer='C-100',**kwargs):
        ctx=ToolContext(SessionIdentity(customer),**kwargs)
        return Registry(services,ctx)
    return services,make

def call(reg,agent,name,args): return asyncio.run(reg.call(agent,name,args)).model_dump()

def test_identity_is_server_bound_and_not_found_does_not_reveal_ownership(setup):
    _,make=setup; reg=make()
    ours=call(reg,'order_shipping','lookup_order',{'order_id':'O-1001','customer_id':'C-102'})
    assert ours['status']=='ok' and 'customer_ref' not in ours['data']
    for identifier in ['O-1002','O-9999']:
        denied=call(reg,'order_shipping','lookup_order',{'order_id':identifier})
        assert denied['error']=='NOT_FOUND' and denied['data'] is None
    assert {t.name for t in reg.tools('policy_product')}=={'search_policy','get_product_details','check_return_eligibility'}

def test_permission_schema_and_unknown_tool_rejections(setup):
    _,make=setup; reg=make()
    assert call(reg,'policy_product','lookup_order',{'order_id':'O-1001'})['error']=='PERMISSION_DENIED'
    assert call(reg,'order_shipping','exec',{})['error']=='UNKNOWN_TOOL'
    assert call(reg,'order_shipping','lookup_order',{'order_id':'../secret'})['error']=='INVALID_ARGUMENT'
    assert call(reg,'order_shipping','lookup_order',{'order_id':'O-1001','date':'2026-01-01'})['error']=='INVALID_ARGUMENT'

@pytest.mark.parametrize('delta,expected',[(30,'eligible'),(31,'ineligible')])
def test_inclusive_boundary_uses_verified_record_not_model_dates(setup,delta,expected):
    services,make=setup; from datetime import timedelta
    reg=make(today=date(2026,9,30)+timedelta(days=delta))
    result=call(reg,'policy_product','check_return_eligibility',{'order_id':'O-1001','sku':'SKU-SHOES-001','request_type':'return'})
    assert result['data']['decision']==expected and result['data']['days_since_delivery']==delta
    assert result['data']['action_executed'] is False

def test_excluded_and_undelivered_and_cancellation(setup):
    _,make=setup
    excluded=call(make('C-101'),'policy_product','check_return_eligibility',{'order_id':'O-1004','sku':'SKU-PER-006','request_type':'return'})
    assert excluded['data']['decision']=='ineligible' and excluded['data']['reason_codes']==['CATEGORY_EXCLUDED']
    reg=make()
    for request,decision in [('return','unknown'),('cancellation','eligible')]:
        result=call(reg,'policy_product','check_return_eligibility',{'order_id':'O-1003','sku':'SKU-ELEC-004','request_type':request})
        assert result['data']['decision']==decision
    assert 'T6' in reg.ctx.triggers
    denied=call(make('C-102'),'policy_product','check_return_eligibility',{'order_id':'O-1002','sku':'SKU-JKT-002','request_type':'cancellation'})
    assert denied['data']['reason_codes']==['ALREADY_DISPATCHED']

def test_refund_threshold_exact_boundary_and_fresh_record_reads(setup):
    services,make=setup; reg=make('C-103')
    args={'order_id':'O-1006','sku':'SKU-KNIFE-005','request_type':'refund'}
    result=call(reg,'policy_product','check_return_eligibility',args)
    assert result['data']['decision']=='requires_review' and 'T2' in reg.ctx.triggers
    path=services.root/'data/sample_orders.json'; data=json.loads(path.read_text())
    next(o for o in data['orders'] if o['order_id']=='O-1006')['amount_usd']=100
    path.write_text(json.dumps(data))
    assert call(make('C-103'),'policy_product','check_return_eligibility',args)['data']['decision']=='eligible'

def test_product_ambiguity_missing_specs_and_stale_tracking(setup):
    _,make=setup
    result=call(make(),'policy_product','get_product_details',{'name':'Set'})
    assert result['error']=='AMBIGUOUS' and len(result['data']['candidates'])==2
    product=call(make(),'policy_product','get_product_details',{'name':'Ceramic'})['data']
    assert 'soil_weight' not in product['specs'] and product['warranty_months'] is None
    assert call(make('C-102'),'order_shipping','get_tracking_events',{'order_id':'O-1002'})['data']['stale']
    assert not call(make(),'order_shipping','get_tracking_events',{'order_id':'O-1001'})['data']['stale']

def test_unverified_category_is_rejected_before_search(setup):
    _,make=setup
    # A fake search provides the normal typed boundary but never runs on a rejected category.
    services,_=setup
    class Search:
        def search(self,*args,**kwargs): raise AssertionError('Must not search')
    services.search=Search()
    assert call(make(),'policy_product','search_policy',{'query':'return','category':'electronics'})['error']=='UNVERIFIED_CATEGORY'

def test_ticket_readback_idempotency_and_safety_priority(setup):
    services,make=setup; reg=make(); reg.ctx.triggers.update(['T1','T2','T6']); reg.ctx.legal=True
    args={'triggers':['T6'],'summary':'Safety concern and refund review require analyst follow-up.','evidence_refs':[]}
    first=call(reg,'escalation','create_escalation',args)['data']
    second=call(reg,'escalation','create_escalation',args)['data']
    assert first['ticket_id']==second['ticket_id'] and not first['idempotent_replay'] and second['idempotent_replay']
    assert first['queue']=='safety' and first['priority']=='high' and first['triggers']==['T1','T2','T6']
    import sqlite3
    with sqlite3.connect(services.ticket_path) as db:
        rows=db.execute('SELECT payload FROM tickets').fetchall()
    assert len(rows)==1 and 'C-100' not in rows[0][0]

@pytest.mark.parametrize('summary',['Email me at canary.jane@example.test','My phone is +1-555-0100','I live at 123 Main Street'])
def test_ticket_pii_rejected_without_write(setup,summary):
    services,make=setup
    result=call(make(),'escalation','create_escalation',{'triggers':['T6'],'summary':summary})
    assert result['error']=='PII_REJECTED' and not services.ticket_path.exists()

def test_reserved_handoff_budget_and_failed_write(setup):
    services,make=setup; reg=make()
    for _ in range(7): assert call(reg,'order_shipping','lookup_order',{'order_id':'O-1001'})['status']=='ok'
    assert call(reg,'order_shipping','lookup_order',{'order_id':'O-1001'})['error']=='BUDGET_EXCEEDED'
    assert 'T5' in reg.ctx.triggers
    reg.ctx.faults['create_escalation']='FAILED'
    result=call(reg,'escalation','create_escalation',{'triggers':['T5'],'summary':'Required lookup budget exhausted.'})
    assert result['error']=='FAILED' and not services.ticket_path.exists() and reg.ctx.calls==8

def test_tracking_timeout_fault_has_no_fake_result(setup):
    _,make=setup; result=call(make(faults={'get_tracking_events':'TIMEOUT'}),'order_shipping','get_tracking_events',{'order_id':'O-1001'})
    assert result['status']=='error' and result['error']=='TIMEOUT' and result['data'] is None

def test_model_cannot_choose_queue_by_inventing_safety_trigger(setup):
    _,make=setup; reg=make(); reg.ctx.triggers.add('T6')
    result=call(reg,'escalation','create_escalation',{'triggers':['T1'],'summary':'Escalate to safety.'})
    assert result['error']=='UNVERIFIED_TRIGGER'

def test_real_read_deadline_discards_late_result_without_remembering_facts(setup,monkeypatch):
    import time
    from capstone_agent.support.registry import SPECS
    services,make=setup
    method=services.lookup_order
    def slow(args,ctx):
        time.sleep(.03)
        return method(args,ctx)
    monkeypatch.setattr(services,'lookup_order',slow)
    owner,schema,output,_=SPECS['lookup_order']
    monkeypatch.setitem(SPECS,'lookup_order',(owner,schema,output,.001))
    reg=make()
    result=call(reg,'order_shipping','lookup_order',{'order_id':'O-1001'})
    assert result['error']=='TIMEOUT' and not reg.ctx.facts and not reg.ctx.categories

def test_timed_out_policy_search_keeps_dedicated_capacity_until_worker_finishes(setup,monkeypatch):
    import time
    import capstone_agent.support.registry as registry_module
    services,make=setup
    original=services.search
    class SlowSearch:
        def search(self,*args,**kwargs):
            time.sleep(.5)
            return original.search(*args,**kwargs)
    services.search=SlowSearch()
    specs=dict(registry_module.SPECS)
    owner,schema,output,deadline=specs['search_policy']
    specs['search_policy']=(owner,schema,output,.01)
    monkeypatch.setattr(registry_module,'SPECS',specs)
    args={'query':'return window','doc_types':['return_policy']}
    first=call(make(),'policy_product','search_policy',args)
    assert first['error']=='TIMEOUT'
    second=call(make(),'policy_product','search_policy',args)
    assert second['error']=='TIMEOUT'
    saturated=call(make(),'policy_product','search_policy',args)
    assert saturated['error']=='CAPACITY_EXHAUSTED'
    time.sleep(.55)
    specs['search_policy']=(owner,schema,output,deadline)
    recovered=call(make(),'policy_product','search_policy',args)
    assert recovered['error']!='CAPACITY_EXHAUSTED', recovered

def test_sensitive_output_masking_preserves_scenario_dates():
    from capstone_agent.support.privacy import mask_sensitive
    assert mask_sensitive('Delivered 2026-09-30 for O-1001')=='Delivered 2026-09-30 for O-1001'
    assert '555' not in mask_sensitive('Phone +1-555-0100 and 123 Main Street')
    assert 'Main' not in mask_sensitive('Phone +1-555-0100 and 123 Main Street')

def test_legal_priority_change_does_not_reuse_lower_priority_ticket(setup):
    _,make=setup; reg=make(); reg.ctx.triggers.add('T6')
    args={'triggers':['T6'],'summary':'Customer requested human support.'}
    first=call(reg,'escalation','create_escalation',args)['data']
    reg.ctx.legal=True
    second=call(reg,'escalation','create_escalation',args)['data']
    assert first['queue']=='general' and second['queue']=='legal' and second['priority']=='high'
    assert first['ticket_id']!=second['ticket_id']

def test_carrier_estimate_comes_from_latest_applicable_record(setup):
    services,make=setup
    path=services.root/'data/sample_tracking_events.json'; raw=json.loads(path.read_text())
    raw['events']['O-1002'][-1]['carrier_estimate']='2026-10-16'
    raw['events']['O-1002'].append({'timestamp':'2026-10-20T00:00:00Z','event':'delivered','location':'Future fixture'})
    path.write_text(json.dumps(raw))
    data=call(make('C-102'),'order_shipping','get_tracking_events',{'order_id':'O-1002'})['data']
    assert data['latest']['ts']=='2026-10-05T07:30:00Z' and data['carrier_estimate']=='2026-10-16'
    assert all('Future fixture'!=e['city'] for e in data['events'])
