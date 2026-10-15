"""Bounded Phase 5 scan: runtime and synthetic support artifacts, no uploads."""
import json
from pathlib import Path
from capstone_agent.config import load_environment
ROOT=Path(__file__).resolve().parents[1]

def main():
    env=load_environment(ROOT/'.env')
    probes={'email_canary':'canary.jane@example.test','phone_canary':'+1-555-0100','address_canary':'123 Main Street','ssn_canary':'123-45-6789'}
    probes.update({name:env[name] for name in ['MODEL_API_KEY','LLM_API_KEY','LANGSMITH_API_KEY','OPENAI_API_KEY'] if env.get(name)})
    findings=[]; files=0
    for directory in [ROOT/'data/runtime',ROOT/'artifacts/phase5_runs']:
        for path in directory.rglob('*') if directory.exists() else []:
            if not path.is_file(): continue
            files+=1; data=path.read_bytes()
            for name,value in probes.items():
                if value.encode() in data: findings.append({'file':str(path.relative_to(ROOT)),'probe':name})
    report={'files_scanned':files,'findings':findings,'passed':not findings,
            'limits':'Known canaries and configured credentials in Phase 5 stores/artifacts only; not universal PII detection or hosted tracing verification.'}
    destination=ROOT/'artifacts/phase5_privacy_scan.json'
    destination.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    return 1 if findings else 0

if __name__=='__main__': raise SystemExit(main())
