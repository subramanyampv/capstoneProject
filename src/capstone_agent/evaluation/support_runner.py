"""Final-graph run recorder and deterministic DeepEval contract metric.

Expected routing/semantic labels and reviewed identity contexts remain Phase 9 work.
"""
import hashlib
import json
import os
from pathlib import Path
os.environ['DEEPEVAL_DISABLE_DOTENV']='1'
os.environ['DEEPEVAL_TELEMETRY_OPT_OUT']='YES'
from deepeval.metrics import BaseMetric
from capstone_agent.support.contracts import ResponseDraft, evidence_ref_key

class SupportContractMetric(BaseMetric):
    threshold=1;async_mode=False;evaluation_cost=0
    @property
    def __name__(self):return 'Final support code contract (not semantic correctness)'
    def measure(self,test_case,**kwargs):
        try:
            result=json.loads(test_case.actual_output);draft=ResponseDraft.model_validate(result['response'])
            refs={evidence_ref_key(ref) for row in result['tool_records'] if row['status']=='ok' for ref in row['evidence_refs']}
            cited={evidence_ref_key(ref) for ref in draft.citations}
            ok=(draft.outcome_claimed==result['outcome'] and cited<=refs
                and result['model_calls']<=12 and result['tool_calls']<=8 and result['handoffs']<=4 and result['replans']<=1 and result['repairs']<=1)
            if result['outcome'] in {'ESCALATED','BUDGET_EXHAUSTED_ESCALATED'}:
                ok=ok and result['ticket'] and result['ticket']['status']=='created'
                ok=ok and any(row['name']=='create_escalation' and row['status']=='ok' and row['data'].get('ticket_id')==result['ticket']['ticket_id'] for row in result['tool_records'])
            if result['outcome']=='ESCALATION_FAILED_DISCLOSED':ok=ok and not(result['ticket'] and result['ticket'].get('status')=='created')
            if result['triggers']:ok=ok and result['outcome'] in {'ESCALATED','BUDGET_EXHAUSTED_ESCALATED','ESCALATION_FAILED_DISCLOSED'}
            expected=(test_case.metadata or {}).get('expected_outcome')
            if expected:ok=ok and result['outcome']==expected
            self.success=bool(ok)
        except (ValueError,KeyError,TypeError,AttributeError):self.success=False
        self.score=float(self.success);self.reason='Typed/budget/evidence/handoff assertions only; no semantic faithfulness or routing grade.'
        return self.score
    async def a_measure(self,test_case,**kwargs):return self.measure(test_case,**kwargs)
    def is_successful(self):return self.success


def load_cases(path,*,contexts=None,allow_holdout=False):
    path=Path(path)
    if 'holdout' in path.name.lower() and not allow_holdout:raise ValueError('HOLDOUT_REQUIRES_EXPLICIT_OPT_IN')
    data=json.loads(path.read_text());cases=data.get('cases') if isinstance(data,dict) else data
    if not isinstance(cases,list) or not cases:raise ValueError('INVALID_EVALUATION_CASES')
    contexts=contexts or {}
    result=[]
    for case in cases:
        if not isinstance(case,dict) or not isinstance(case.get('id'),str) or not isinstance(case.get('input'),str):raise ValueError('INVALID_EVALUATION_CASE')
        context=contexts.get(case['id'],{})
        customer=context.get('customer_id',case.get('customer_id'))
        if customer not in {'C-100','C-101','C-102','C-103'}:raise ValueError('REVIEWED_CUSTOMER_CONTEXT_REQUIRED')
        setup=context.get('setup_turns',[])
        if not isinstance(setup,list) or len(setup)>10 or any(not isinstance(query,str) or len(query)>2000 for query in setup):raise ValueError('INVALID_SETUP_TURNS')
        result.append({**case,'customer_id':customer,'setup_turns':setup})
    return result


def run_evaluation(dataset,output,*,contexts=None,allow_holdout=False,repeats=1,dry_run=False):
    if not 1<=repeats<=5:raise ValueError('INVALID_REPEAT_COUNT')
    cases=load_cases(dataset,contexts=contexts,allow_holdout=allow_holdout)
    manifest={'case_count':len(cases),'repeats':repeats,'dataset_sha256':hashlib.sha256(Path(dataset).read_bytes()).hexdigest(),
        'limits':'Code contracts only. Reviewed identity/setup contexts and semantic/expected routing labels require Phase 9 review. Holdout must never be used for tuning.'}
    if dry_run:return manifest
    from capstone_agent.config import LLMConfig
    from capstone_agent.retrieval.configured_embeddings import ConfiguredEmbeddings
    from capstone_agent.retrieval.chroma_store import PolicySearch
    from capstone_agent.support.runtime import run_support
    from capstone_agent.support.registry import SessionIdentity
    from capstone_agent.support.memory import SessionMemory
    from capstone_agent.support.preferences import PreferenceStore
    from capstone_agent.support.privacy import minimize
    from capstone_agent.support.services import ROOT
    from deepeval.test_case import LLMTestCase
    import tempfile
    config=LLMConfig.from_env(ROOT/'.env');search=PolicySearch(ConfiguredEmbeddings());search.search('return policy')
    output=Path(output);output.mkdir(parents=True,exist_ok=False);scores=[]
    with tempfile.TemporaryDirectory() as local:
        store=PreferenceStore(Path(local))
        for case in cases:
            for repeat in range(repeats):
                store.forget(case['customer_id'])
                identity=SessionIdentity(case['customer_id']);memory=SessionMemory()
                try:
                    for query in case['setup_turns']:run_support(query,identity=identity,search=search,memory=memory,preferences=store)
                    response=run_support(case['input'],identity=identity,search=search,memory=memory,preferences=store)
                finally:memory.close()
                metric=SupportContractMetric();metric.measure(LLMTestCase(input='synthetic support case',actual_output=json.dumps(response),metadata={'expected_outcome':case.get('expected_outcome')}))
                row={'case_id':case['id'],'repeat':repeat,'score':metric.score,'result':response}
                # Case IDs are user-supplied; never use them as output paths.
                with (output/'outputs.jsonl').open('a') as stream:stream.write(minimize(json.dumps(row),(config.api_key,))+'\n')
                scores.append(metric.score)
    manifest.update(runs=len(scores),contract_passes=sum(scores));(output/'summary.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest
