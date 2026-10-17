"""Submission snapshots exclude secrets/history and use committed source bytes."""
import importlib
import subprocess
import sys
import zipfile
from pathlib import Path
import pytest


def test_snapshot_keeps_committed_source_and_rejects_tracked_credentials(tmp_path,monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[2]/'scripts'))
    package=importlib.import_module('package_source')
    repo=tmp_path/'source';repo.mkdir()
    def git(*args):return subprocess.run(['git',*args],cwd=repo,check=True,capture_output=True)
    git('init');git('config','user.name','Snapshot Test');git('config','user.email','snapshot@example.invalid')
    secret='synthetic-snapshot-canary-credential-123456'
    (repo/'.env').write_text('TEST_API_KEY='+secret+'\n')
    (repo/'.env.example').write_text('TEST_API_KEY=\n')
    (repo/'app.py').write_text('COMMITTED = True\n')
    (repo/'start.sh').write_text('#!/bin/sh\nexit 0\n');(repo/'start.sh').chmod(0o755)
    (repo/'data/runtime').mkdir(parents=True);(repo/'data/runtime/private.txt').write_text(secret)
    git('add','.');git('commit','-m','Synthetic snapshot fixture')
    (repo/'app.py').write_text('UNCOMMITTED = True\n')
    archive=tmp_path/'snapshot.zip'
    monkeypatch.setattr(package,'ROOT',repo)
    monkeypatch.setattr(sys,'argv',['package_source.py','--output',str(archive)])
    package.main()
    with zipfile.ZipFile(archive) as saved:
        assert saved.read('capstone_agent/app.py')==b'COMMITTED = True\n'
        assert 'capstone_agent/.env.example' in saved.namelist()
        assert not any(name.endswith('/.env') or '/.git/' in name or '/data/runtime/' in name for name in saved.namelist())
        assert saved.getinfo('capstone_agent/start.sh').external_attr>>16 & 0o111
    (repo/'app.py').write_text('SECRET = '+repr(secret)+'\n');git('add','app.py');git('commit','-m','Synthetic rejection fixture')
    with pytest.raises(ValueError,match='CONFIGURED_CREDENTIAL_FOUND_IN_SOURCE'):package.main()
