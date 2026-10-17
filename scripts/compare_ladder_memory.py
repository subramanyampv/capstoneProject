"""Current tools/guards ladder arm with memory explicitly off on the same ten cases."""
import argparse
import hashlib
import json
import tempfile
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
from run_final_suite import build_hashes,SerializedSearch
from build_capability_ladder import IDS
from capstone_agent.config import LLMConfig,load_environment
from capstone_agent.evaluation.export import minimized_json,verified_tickets
from capstone_agent.retrieval.chroma_store import PolicySearch
from capstone_agent.retrieval.embeddings_voyage import VoyageNanoEmbeddings
from capstone_agent.support.runtime import run_support
from capstone_agent.support.memory import SessionMemory
from capstone_agent.support.preferences import PreferenceStore
from capstone_agent.support.registry import SessionIdentity
from capstone_agent.observability.support_tracing import EXPORTER

ROOT=Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser();parser.add_argument('final_run',type=Path);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    manifest=json.loads((args.final_run/'manifest.json').read_text());locked=build_hashes()
    if locked!=manifest['build_sha256']:raise ValueError('FINAL_BUILD_MUST_MATCH_LADDER_ARM')
    final={row['case_id']:row for row in map(json.loads,(args.final_run/'outputs.jsonl').read_text().splitlines())}
    cases={row['id']:row for row in json.loads((ROOT/'data/evaluation_cases.json').read_text())['cases']}
    contexts=json.loads((ROOT/'evaluation/phase9'/manifest['context_file']).read_text())
    config=LLMConfig.from_env(ROOT/'.env')
    fingerprint=hashlib.sha256(json.dumps({'settings':config.public_settings(),'endpoint':config.base_url},sort_keys=True).encode()).hexdigest()
    if fingerprint!=manifest['model_config_sha256']:raise ValueError('LADDER_MODEL_MUST_MATCH_FINAL_RUN')
    env=load_environment(ROOT/'.env');secrets=tuple(value for name,value in env.items() if name.endswith('API_KEY') and value)
    search=SerializedSearch(PolicySearch(VoyageNanoEmbeddings()));search.search('return policy')
    def run(ident):
        if build_hashes()!=locked:raise ValueError('BUILD_CHANGED_DURING_LADDER')
        case=cases[ident];context=contexts[ident];memory=SessionMemory();identity=SessionIdentity(context['customer_id'])
        with tempfile.TemporaryDirectory() as local:
            preferences=PreferenceStore(Path(local))
            try:
                setup=[run_support(query,identity=identity,search=search,memory=memory,memory_enabled=False,preferences=preferences) for query in context.get('setup_turns',[])]
                result=run_support(case['input'],identity=identity,search=search,memory=memory,memory_enabled=False,preferences=preferences)
            finally:memory.close()
        expected_hash=hashlib.sha256(case['input'].encode()).hexdigest()
        if final[ident]['input_sha256']!=expected_hash:raise ValueError('PAIRED_INPUT_MISMATCH')
        return {'case_id':ident,'input_sha256':expected_hash,'setup_results':setup,'result':result,
            'paired_memory_on_outcome':final[ident]['result']['outcome'],
            'memory_off_confirmed':not result['memory']['enabled'],
            'paired_memory_on_confirmed':final[ident]['result']['memory']['enabled']}
    records=[]
    with ThreadPoolExecutor(max_workers=3) as pool:
        for future in as_completed([pool.submit(run,ident) for ident in IDS]):
            row=future.result();records.append(row);print(row['case_id'],row['result']['outcome'],flush=True)
    ids=tuple(ident for row in records for item in [row['result'],*row['setup_results']] for ident in verified_tickets(item))
    report={'final_run':args.final_run.name,'stage':'tools_guards_memory_explicitly_off','workers':3,'model_settings':config.public_settings(),
        'paired_build_verified':True,'isolated_preferences_and_sessions':True,'comparisons':records,
        'limits':'Current tools/guards arm uses unchanged frozen questions, customer identities and setup turns; only session retention is explicitly disabled. Compare to recorded final-run memory-on outputs. Historical baseline/LLM/RAG stages still differ in prompts, dates and evidence access, so the complete ladder is not a causal accuracy estimate. This arm is not scored as final-system acceptance. Holdout is not read.'}
    exported=json.loads(minimized_json(report,secrets,verified_ticket_ids=ids))
    for row,clean in zip(records,exported['comparisons']):clean['input_sha256']=row['input_sha256']
    exported['build_sha256']=locked
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(exported,indent=2)+'\n');EXPORTER.wait(10)

if __name__=='__main__':main()
