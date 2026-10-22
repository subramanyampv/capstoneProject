"""Scanned source exports do not require Git or silently skip ignored copies."""
import importlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[2]
SYNTHETIC_CREDENTIAL = 'synthetic-scanner-credential-for-tests'


@pytest.fixture(params=['scan_final', 'scan_phase9'])
def scanner(request, tmp_path, monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / 'scripts'))
    module = importlib.import_module(request.param)
    monkeypatch.setattr(module, 'ROOT', tmp_path)
    monkeypatch.setattr(module, 'load_environment', lambda path: {'LLM_API_KEY': SYNTHETIC_CREDENTIAL})
    run_dir = tmp_path / 'artifacts' / 'current_run'
    monkeypatch.setattr('sys.argv', [request.param, str(run_dir)] if request.param == 'scan_phase9' else [request.param])
    report = run_dir / 'privacy_scan.json' if request.param == 'scan_phase9' else tmp_path / 'artifacts/phase8/privacy_scan.json'
    return module, report


def git_listing(monkeypatch, mode):
    def run(*args, **kwargs):
        if mode == 'missing':
            raise FileNotFoundError('Synthetic missing Git executable')
        return SimpleNamespace(returncode=128 if mode == 'history_free' else 0, stdout=b'')
    monkeypatch.setattr('subprocess.run', run)


@pytest.mark.parametrize('mode', ['history_free', 'ignored_export', 'missing'])
def test_detects_configured_credential_in_export_with_unusable_git(scanner, tmp_path, monkeypatch, capsys, mode):
    module, report = scanner
    git_listing(monkeypatch, mode)
    source = tmp_path / 'src' / 'example.py'
    source.parent.mkdir()
    source.write_text('value = ' + repr(SYNTHETIC_CREDENTIAL) + '\n')
    assert module.main() == 1
    result = json.loads(report.read_text())
    assert result['source_files'] >= 1
    assert {'file': 'src/example.py', 'probe': 'LLM_API_KEY'} in result['findings']
    assert SYNTHETIC_CREDENTIAL not in capsys.readouterr().out


def test_clean_export_without_git_excludes_private_configuration_and_creates_output_parents(scanner, tmp_path, monkeypatch):
    module, report = scanner
    git_listing(monkeypatch, 'missing')
    (tmp_path / 'public.py').write_text('SAFE = True\n')
    for name in ('.env', '.env.local', '.git/config', '.venv/private.txt', 'venv/private.txt',
                 'env/private.txt', 'node_modules/private.txt', '.cache/private.txt',
                 'knowledge/index/private.txt', 'knowledge/index_manifest.json'):
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(SYNTHETIC_CREDENTIAL)
    assert not report.parent.exists()
    assert module.main() == 0
    result = json.loads(report.read_text())
    assert result['passed'] and result['findings'] == [] and result['source_files'] == 1


def test_git_listing_still_filters_private_paths_and_source_symlinks(tmp_path, monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / 'scripts'))
    module = importlib.import_module('scan_final')
    for name in ('public.py', '.env', 'knowledge/index/private.txt', 'data/runtime/requests.jsonl'):
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('synthetic')
    (tmp_path / 'linked.py').symlink_to(tmp_path / '.env')
    monkeypatch.setattr('subprocess.run', lambda *args, **kwargs: SimpleNamespace(
        returncode=0, stdout=b'public.py\0.env\0knowledge/index/private.txt\0data/runtime/requests.jsonl\0linked.py\0'))
    assert module.source_files(tmp_path) == {'public.py'}


def test_private_runtime_remains_scanned_separately(scanner, tmp_path, monkeypatch):
    module, report = scanner
    git_listing(monkeypatch, 'missing')
    path = tmp_path / 'data/runtime/requests.jsonl'
    path.parent.mkdir(parents=True)
    path.write_text(SYNTHETIC_CREDENTIAL)
    assert module.main() == 1
    result = json.loads(report.read_text())
    assert result['source_files'] == 0 and result['runtime_files'] == 1
    assert {'file': 'data/runtime/requests.jsonl', 'probe': 'LLM_API_KEY'} in result['findings']
