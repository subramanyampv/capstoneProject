"""Safe startup report and metadata-only operational summaries."""
import json
import math
from pathlib import Path
from capstone_agent.config import LLMConfig,load_environment,show_deferred_ui
from capstone_agent.observability.langsmith_tracing import ObservabilityConfig
from capstone_agent.support.services import ROOT,Services
from capstone_agent.support.guards import SafetyRules


def doctor(root=ROOT,*,index=False):
    checks=[]
    def check(name,execute):
        try:execute();checks.append({'check':name,'passed':True})
        except Exception:checks.append({'check':name,'passed':False,'error':'CHECK_FAILED'})
    check('model_configuration',lambda:LLMConfig.from_env(root/'.env'))
    check('safety_rules',lambda:SafetyRules(root/'config/safety_rules.json'))
    check('policy_fixture_consistency',lambda:Services(root=root))
    def flags():
        values=load_environment(root/'.env')
        if values.get('MEMORY_ENABLED','true').strip().lower() not in {'true','false'}:raise ValueError('INVALID_FLAG')
        show_deferred_ui(root/'.env')
    check('runtime_flags',flags)
    check('observability_configuration',lambda:ObservabilityConfig.from_env(root/'.env'))
    if index:
        def retrieval():
            from capstone_agent.retrieval.embeddings_voyage import VoyageNanoEmbeddings
            from capstone_agent.retrieval.chroma_store import PolicySearch
            search=PolicySearch(VoyageNanoEmbeddings(),root=root);search.search('return policy')
        check('pinned_embedding_and_index',retrieval)
    return {'passed':all(c['passed'] for c in checks),'checks':checks,
        'limits':'Configuration/local assets only; no provider connectivity, hosted ingestion or final acceptance claim.'}


def operational_summary(records):
    groups={}
    for row in records:
        outcome=row.get('outcome','REQUEST_REJECTED')
        group=groups.setdefault(outcome,[]);group.append(row)
    output={}
    def percentile(values,p):
        if not values:return None
        values=sorted(values);position=(len(values)-1)*p;low=int(position);high=math.ceil(position)
        return round(values[low]+(values[high]-values[low])*(position-low),3)
    for name,rows in groups.items():
        times=[r['latency_ms'] for r in rows if type(r.get('latency_ms')) in {int,float}]
        output[name]={'requests':len(rows),'latency_ms_p50':percentile(times,.5),'latency_ms_p95':percentile(times,.95),
            'tokens':sum(r.get('tokens',0) for r in rows),'repairs':sum(r.get('repairs',0) for r in rows),
            'tool_errors':sum(t.get('status')=='error' for r in rows for t in r.get('tools',[]))}
    return {'paths':output,'limits':'Observed samples by terminal outcome, interpolated percentiles; not a production latency SLA.'}
