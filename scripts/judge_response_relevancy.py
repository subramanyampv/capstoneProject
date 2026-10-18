"""Versioned prose-relevancy diagnostic; preserves primary structured-response scores."""
import argparse
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor,as_completed
from dataclasses import replace
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PROTOCOL='response-prose-relevancy-v2'


def projection(row,question,setup_turns):
    response=row['result']['response']
    output='\n'.join([response['answer'],*response['why'],*response['next_steps']])
    # Include declared prior conversation for pronouns and reset-dependent turns.
    prior=[]
    for question_before,answer_before in zip(setup_turns,row.get('setup_results',[])):
        prior.append({'user':question_before,'assistant':answer_before['response']['answer']})
    query=json.dumps({'prior_conversation':prior,'current_user_request':question}) if prior else question
    return query,output


def main():
    from judge_final_suite import FinalJudge
    from capstone_agent.config import LLMConfig,load_environment
    from capstone_agent.evaluation.export import minimized_json,verified_tickets
    from capstone_agent.support.privacy import minimize
    from deepeval.metrics import AnswerRelevancyMetric
    from deepeval.test_case import LLMTestCase
    parser=argparse.ArgumentParser();parser.add_argument('run_dir',type=Path);parser.add_argument('--workers',type=int,choices=[1,2,3],default=3);args=parser.parse_args()
    run=args.run_dir;outputs=run/'outputs.jsonl';sha=hashlib.sha256(outputs.read_bytes()).hexdigest()
    rows=[json.loads(s) for s in outputs.read_text().splitlines()]
    if len(rows)!=65 or len({r['case_id'] for r in rows})!=65:raise ValueError('COMPLETE_FROZEN_RUN_REQUIRED')
    manifest=json.loads((run/'manifest.json').read_text())
    originals={r['id']:r for r in json.loads((ROOT/'data/evaluation_cases.json').read_text())['cases']}
    contexts=json.loads((ROOT/'evaluation/phase9'/manifest['context_file']).read_text())
    env=load_environment(ROOT/'.env');app=LLMConfig.from_env(ROOT/'.env')
    if any(env.get(k) for k in ['JUDGE_MODEL','JUDGE_API_KEY','JUDGE_BASE_URL']):
        config=LLMConfig(base_url=env.get('JUDGE_BASE_URL',''),model=env.get('JUDGE_MODEL',''),api_key=env.get('JUDGE_API_KEY',''),max_completion_tokens=2400,max_retries=0,temperature=0,enable_thinking=app.enable_thinking)
    else:config=replace(app,max_completion_tokens=2400,max_retries=0,temperature=0)
    secrets=tuple(v for k,v in env.items() if k.endswith('API_KEY') and v)
    lock={'protocol':PROTOCOL,'source_outputs_sha256':sha,'recorder_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'judge_settings':config.public_settings(),'judge_fingerprint':hashlib.sha256(json.dumps({'settings':config.public_settings(),'endpoint':config.base_url},sort_keys=True).encode()).hexdigest(),
        'projection':'answer + why + next_steps; references/intent/outcome metadata omitted; declared prior conversation included',
        'limits':'Additional diagnostic motivated by primary scores penalizing metadata. Primary v1 scores remain unchanged. Same-model judging is not independent human assessment. Streamlit displays prose plus separate sources; terminal JSON also exposes metadata. This diagnostic does not replace full-envelope groundedness or establish a causal improvement.'}
    manifest_path=run/'relevancy_v2_manifest.json'
    if manifest_path.exists() and json.loads(manifest_path.read_text())!=lock:raise ValueError('DIAGNOSTIC_RESUME_LOCK_CHANGED')
    manifest_path.write_text(json.dumps(lock,indent=2)+'\n')
    target=run/'relevancy_v2.jsonl';done={json.loads(s)['case_id'] for s in target.read_text().splitlines()} if target.exists() else set()
    def judge(row):
        query,output=projection(row,originals[row['case_id']]['input'],contexts[row['case_id']].get('setup_turns',[]))
        evaluator=FinalJudge(config);evaluator.verified_ids=verified_tickets(row['result'])
        try:
            metric=AnswerRelevancyMetric(threshold=.8,model=evaluator,async_mode=False,include_reason=True)
            metric.measure(LLMTestCase(input=minimize(query,secrets),actual_output=minimize(output,secrets,verified_ticket_ids=evaluator.verified_ids)))
            return {'case_id':row['case_id'],'score':metric.score,'passed':metric.is_successful(),'status':'measured','reason':minimize(metric.reason or '',secrets),'tokens':evaluator.tokens}
        except Exception as exc:
            return {'case_id':row['case_id'],'score':None,'passed':False,'status':'error','error_category':type(exc).__name__}
        finally:evaluator.client.close()
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for future in as_completed([pool.submit(judge,row) for row in rows if row['case_id'] not in done]):
            record=future.result()
            with target.open('a') as stream:stream.write(minimized_json(record,secrets)+'\n')
            print(record['case_id'],record['score'],record['status'],flush=True)
    if hashlib.sha256(outputs.read_bytes()).hexdigest()!=sha:raise ValueError('DIAGNOSTIC_OUTPUTS_CHANGED')
    scores=[json.loads(s) for s in target.read_text().splitlines()];measured=[r for r in scores if r['status']=='measured']
    summary={**lock,'cases':len(scores),'measured':len(measured),'errors':len(scores)-len(measured),
        'mean':sum(r['score'] for r in measured)/len(measured) if measured else None,'above_threshold':sum(r['passed'] for r in measured)}
    (run/'relevancy_v2_summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps({k:summary[k] for k in ['cases','measured','errors','mean','above_threshold']}))

if __name__=='__main__':main()
