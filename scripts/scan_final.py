"""Current-key scan of source/evidence plus canaries in current final operational stores."""
import json
import subprocess
import os
from pathlib import Path
from capstone_agent.config import load_environment
ROOT=Path(__file__).resolve().parents[1]

def main():
    env=load_environment(ROOT/'.env');keys={name:value for name,value in env.items() if name.endswith('API_KEY') and value}
    tracked=subprocess.run(['git','ls-files','-co','--exclude-standard','-z'],cwd=ROOT,capture_output=True)
    if tracked.returncode==0:source=set(tracked.stdout.decode().split('\0'))-{''}
    else:
        # Submission snapshots intentionally contain no Git history or metadata.
        source=set()
        for directory,folders,files in os.walk(ROOT):
            relative=Path(directory).relative_to(ROOT)
            folders[:]=[name for name in folders if name not in {'.git','.venv','.cache','.pytest_cache','__pycache__','submission'}
                and relative/name not in {Path('data/runtime'),Path('knowledge/index')}]
            for name in files:
                if name.startswith('.env') and name!='.env.example':continue
                source.add(str(relative/name))
    canaries={'email':'canary.jane@example.test','phone':'+1-555-0100','address':'123 Main Street','name':'Canary Jordan'}
    findings=[]
    for name in sorted(source):
        path=ROOT/name
        if not path.is_file():continue
        content=path.read_bytes()
        for label,value in keys.items():
            if value.encode() in content:findings.append({'file':name,'probe':label})
    runtime=[path for path in (ROOT/'data/runtime').rglob('*') if path.is_file()]
    final_files=[path for path in (ROOT/'artifacts/phase8').rglob('*') if path.is_file() and path.suffix in {'.json','.jsonl'}]
    for path in runtime+final_files:
        content=path.read_bytes()
        for label,value in {**keys,**canaries}.items():
            if value.encode() in content:findings.append({'file':str(path.relative_to(ROOT)),'probe':label})
    report={'passed':not findings,'source_files':len(source),'runtime_files':len(runtime),'phase8_structured_files':len(final_files),
        'findings':findings,'limits':'Configured credentials in nonignored source/evidence and known canaries in final operational stores/Phase 8 metadata. Historical authored input canaries in test source are intentional. Not a Git-history or universal PII/cloud guarantee; hosted read-back is checked separately.'}
    target=ROOT/'artifacts/phase8/privacy_scan.json';target.parent.mkdir(exist_ok=True);target.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2));return 0 if report['passed'] else 1

if __name__=='__main__':raise SystemExit(main())
