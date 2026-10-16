"""Scan Phase 9 exports without changing historical Phase 8 evidence."""
import argparse
import json
import subprocess
from pathlib import Path
from capstone_agent.config import load_environment

ROOT=Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser();parser.add_argument('run_dir',type=Path);args=parser.parse_args()
    env=load_environment(ROOT/'.env')
    secrets={name:value for name,value in env.items() if name.endswith('API_KEY') and value}
    canaries={'email':'canary.jane@example.test','phone':'+1-555-0100','address':'123 Main Street',
        'name':'Canary Jordan','ssn':'123-45-6789'}
    files=[path for path in args.run_dir.rglob('*') if path.is_file() and path.name!='privacy_scan.json']
    runtime=[path for path in (ROOT/'data/runtime').rglob('*') if path.is_file()]
    findings=[]
    for path in files+runtime:
        content=path.read_bytes()
        for label,value in {**secrets,**canaries}.items():
            if value.encode() in content:findings.append({'file':str(path.relative_to(ROOT)),'probe':label})
    result=subprocess.run(['git','ls-files','-co','--exclude-standard','-z'],cwd=ROOT,capture_output=True,check=True)
    source=set(result.stdout.decode().split('\0'))-{''}
    for name in sorted(source):
        path=ROOT/name
        if not path.is_file():continue
        content=path.read_bytes()
        for label,value in secrets.items():
            if value.encode() in content:findings.append({'file':name,'probe':label})
    report={'passed':not findings,'phase9_files':len(files),'runtime_files':len(runtime),'source_files':len(source),
        'findings':findings,'limits':'Configured keys in nonignored files; known canaries in Phase 9 exports and local runtime. Authored input canaries in tests/datasets intentionally excluded from canary scan. Not a universal PII or hosted-content guarantee. Safety/false-success acceptance is separate.'}
    (args.run_dir/'privacy_scan.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2));return 0 if report['passed'] else 1

if __name__=='__main__':raise SystemExit(main())
