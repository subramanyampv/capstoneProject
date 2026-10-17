"""Build a scanned history-free snapshot of committed files only."""
import argparse
import hashlib
import json
import subprocess
import zipfile
from pathlib import Path
from capstone_agent.config import load_environment

ROOT=Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    listing=subprocess.run(['git','ls-tree','-rz','HEAD'],cwd=ROOT,check=True,capture_output=True).stdout.decode().split('\0')
    tracked={entry.split('\t',1)[1]:entry.split('\t',1)[0].split()[0] for entry in listing if entry}
    env=load_environment(ROOT/'.env');secrets=[value.encode() for key,value in env.items() if key.endswith('API_KEY') and value]
    entries={};excluded=[]
    for name,mode in sorted(tracked.items()):
        path=Path(name)
        if any(part in {'.git','.venv','.cache','__pycache__','.pytest_cache','submission'} for part in path.parts) or name.startswith(('data/runtime/','knowledge/index/')) or (path.name.startswith('.env') and path.name!='.env.example'):
            excluded.append(name);continue
        local=ROOT/path
        if local.is_symlink() or mode=='120000':raise ValueError('SOURCE_SNAPSHOT_REJECTS_SYMLINKS')
        if mode not in {'100644','100755'}:raise ValueError('UNSUPPORTED_SOURCE_ENTRY')
        # Use the committed bytes, never accidentally include uncommitted edits.
        content=subprocess.run(['git','show','HEAD:'+name],cwd=ROOT,check=True,capture_output=True).stdout
        if any(secret in content for secret in secrets):raise ValueError('CONFIGURED_CREDENTIAL_FOUND_IN_SOURCE')
        entries[name]=content
    commit=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,check=True,capture_output=True,text=True).stdout.strip()
    manifest={'commit':commit,'file_count':len(entries),'files':{name:hashlib.sha256(value).hexdigest() for name,value in entries.items()},
        'excluded_tracked_files':excluded,'limits':'Committed source/evidence only; no Git history, .env, local runtime, vector store or model cache. Current configured credentials scanned. Not universal secret detection or proof of release acceptance; use the accompanying evaluation/status documents.'}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(args.output,'w',compression=zipfile.ZIP_DEFLATED) as archive:
        for name,content in {**entries,'SOURCE_SNAPSHOT_MANIFEST.json':json.dumps(manifest,indent=2).encode()}.items():
            info=zipfile.ZipInfo('capstone_agent/'+name,date_time=(2026,10,17,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=int(tracked.get(name,'100644'),8)<<16;archive.writestr(info,content)
    with zipfile.ZipFile(args.output) as archive:
        if archive.testzip() is not None:raise ValueError('ARCHIVE_INTEGRITY_FAILED')
        for name,expected in manifest['files'].items():
            if hashlib.sha256(archive.read('capstone_agent/'+name)).hexdigest()!=expected:raise ValueError('ARCHIVE_CONTENT_MISMATCH')
    report={'archive':args.output.name,'commit':commit,'files':len(entries),'sha256':hashlib.sha256(args.output.read_bytes()).hexdigest(),
        'integrity_checked':True,'current_credentials_found':False,'history_included':False,'release_accepted':False}
    args.output.with_suffix('.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

if __name__=='__main__':main()
