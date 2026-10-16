"""Scan Phase 7 disk artifacts and runtime stores for known canaries/credentials."""
import json
from pathlib import Path
from capstone_agent.config import load_environment
ROOT=Path(__file__).resolve().parents[1]

def main():
    env=load_environment(ROOT/'.env')
    probes={'email_canary':'canary.jane@example.test','phone_canary':'+1-555-0100','address_canary':'123 Main Street','ssn_canary':'123-45-6789'}
    probes.update({name:env[name] for name in ['MODEL_API_KEY','LLM_API_KEY','LANGSMITH_API_KEY','OPENAI_API_KEY'] if env.get(name)})
    files=0;findings=[]
    for directory in [ROOT/'data/runtime',ROOT/'artifacts/style_runs']:
        for path in directory.rglob('*') if directory.exists() else []:
            if not path.is_file():continue
            files+=1;data=path.read_bytes()
            for label,value in probes.items():
                if value.encode() in data:findings.append({'file':str(path.relative_to(ROOT)),'probe':label})
    report={'passed':not findings,'files_scanned':files,'findings':findings,
        'limits':'Known canaries/configured credentials in Phase 7 artifacts and runtime only. Preference deletion is tested separately; this scan does not inspect filesystem remnants. No cloud/universal PII guarantee.'}
    (ROOT/'artifacts/phase7_privacy_scan.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
    return 1 if findings else 0

if __name__=='__main__':raise SystemExit(main())
