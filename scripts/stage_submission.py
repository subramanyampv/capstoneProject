"""Prepare an allowlisted review directory, without creating an archive."""
import argparse
import hashlib
import json
import re
from pathlib import Path

from capstone_agent.config import load_environment

ROOT = Path(__file__).resolve().parents[1]
DATA = ('sample_orders.json', 'sample_tracking_events.json', 'product_catalog.json',
        'policy_rules.json', 'delivery_estimate_rules.json', 'evaluation_cases.json',
        'retrieval_labels.json', 'retrieval_heldout_labels.json')
SCRIPTS = ('check_model.py', 'judge_settings.py', 'run_final_suite.py', 'judge_final_suite.py',
           'compare_judges.py', 'summarize_consistency.py', 'verify_final_tickets.py',
           'replay_submission_demo.py', 'build_submission_evidence.py', 'independent_review_gate.py',
           'judge_response_relevancy.py', 'reuse_identical_human_review.py', 'run_holdout.py',
           'package_source.py', 'scan_final.py', 'scan_phase9.py', 'verify_hosted_tracing.py',
           'evaluate_retrieval.py', 'verify_support_operations.py',
           'ingest.sh', 'run_ui.sh', 'run_support_ui.sh', 'venv.sh')
DOCUMENTS = ('Problem_Framing_Document.md', 'Engineering_And_Product_Justification.md',
             'Debugging_And_Failure_Analysis.md', 'Evaluation_Report.md', 'Demo_Script.md',
             'Retrieval_Proof.md', 'Architecture_Diagrams.md', 'Prompt_Comparison_Report.md')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--evidence-dir', type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    if not output.is_relative_to(ROOT / 'submission') or output.exists():
        raise ValueError('NEW_DIRECTORY_INSIDE_SUBMISSION_REQUIRED')
    entries = {}
    def select(source, destination=None):
        relative = Path(destination or source)
        original = ROOT / source
        if not original.is_file() or original.is_symlink():
            raise ValueError('MISSING_OR_UNSAFE_ALLOWLIST_ENTRY: ' + str(source))
        if relative.is_absolute() or '..' in relative.parts:
            raise ValueError('UNSAFE_DESTINATION')
        entries[str(relative)] = original
    for directory, suffix in [('src', '*.py'), ('tests', '*.py'), ('config', '*.json'), ('knowledge/raw', '*.md')]:
        for path in sorted((ROOT / directory).rglob(suffix)):
            if '__pycache__' not in path.parts:
                select(path.relative_to(ROOT))
    for name in ('pyproject.toml', 'requirements.txt', 'constraints-dev.txt', 'streamlit_app.py', '.env.example', '.gitignore'):
        select(name)
    select('knowledge/index_manifest.json')
    for name in DATA:
        select('data/' + name)
    for name in SCRIPTS:
        select('scripts/' + name)
    for name in ('protocol_v1.json', 'frozen_contexts.json', 'frozen_contexts_v3.json', 'iteration_review_policy_v2.json'):
        select('evaluation/phase9/' + name)
    select('docs/submission/README.md', 'README.md')
    for name in DOCUMENTS:
        select('docs/submission/' + name, 'docs/' + name)
    evidence = args.evidence_dir.resolve()
    if not evidence.is_relative_to(ROOT / 'submission'):
        raise ValueError('DERIVED_SUBMISSION_EVIDENCE_REQUIRED')
    for path in sorted(evidence.glob('*.json')):
        entries['evidence/' + path.name] = path
    if 'evidence/evaluation_summary.json' not in entries:
        raise ValueError('FINAL_DERIVED_EVALUATION_REQUIRED')
    if 'evidence/retrieval_comparison.json' not in entries:
        raise ValueError('DERIVED_RETRIEVAL_PROOF_REQUIRED')
    if not {'evidence/final_case_evidence.json', 'evidence/demo_evidence.json'} <= entries.keys():
        raise ValueError('CASE_AND_DEMO_AUDIT_EVIDENCE_REQUIRED')

    # Resolve probes privately; no configured values are written to the report.
    env = load_environment(ROOT / '.env')
    secrets = {value for name, value in env.items() if name.endswith('API_KEY') and value}
    identities = {env.get(name, '') for name in ('MODEL_NAME', 'LLM_MODEL', 'JUDGE_MODEL')}
    identities.discard('')
    family_probes = {m.group().lower() for identity in identities
                     if (m := re.match(r'[A-Za-z]{4,}', identity.split('/')[-1]))}
    probes = {identity.lower() for identity in identities} | family_probes
    findings = []
    dispositions = []
    contents = {}
    for name, path in entries.items():
        value = path.read_bytes()
        contents[name] = value
        if any(secret.encode() in value for secret in secrets):
            findings.append({'path': name, 'category': 'configured_credential'})
        lower = value.decode('utf-8').lower()
        if name != 'knowledge/index_manifest.json' and any(probe in lower for probe in probes):
            findings.append({'path': name, 'category': 'concrete_model_identity'})
        token_like = bool(re.search(rb'\b(?:sk|api|token)[-_][A-Za-z0-9_-]{20,}', value))
        if token_like:
            item = {'path': name, 'category': 'token_like_literal'}
            (dispositions if name.startswith('tests/') else findings).append(item)
    template = contents['.env.example'].decode()
    if any(line.strip() and not line.lstrip().startswith('#') and
           ('=' not in line or line.split('=', 1)[1].strip()) for line in template.splitlines()):
        findings.append({'path': '.env.example', 'category': 'nonempty_template_assignment'})
    if findings:
        print(json.dumps({'passed': False, 'findings': findings}, indent=2))
        return 1
    output.mkdir(parents=True)
    for name, value in contents.items():
        target = output / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(value)
        target.chmod(entries[name].stat().st_mode & 0o777)
    receipt = {'files': {name: hashlib.sha256(value).hexdigest() for name, value in contents.items()},
               'passed': True, 'configured_credential_findings': 0, 'concrete_model_identity_findings': 0,
               'synthetic_test_fixture_dispositions': dispositions,
               'excluded': ['Git/history', 'virtual environments/dependencies', 'private environment configuration',
                            'model caches', 'runtime databases/raw logs', 'private embedding identity manifest and vector index',
                            'historical source/evidence and superseded documents', 'all protected evaluation datasets and contexts',
                            'assignment/audit PDFs', 'unselected scripts/documents/artifacts'],
               'limits': 'Allowlisted current working-tree source and derived evidence, not a committed snapshot or fresh installation. Configured keys, configured identity/family probes, token-like literals and blank template checked. Synthetic key fixtures in tests are retained. Not universal secret/PII detection; no Git history or protected cases read. Review directory only; no archive or final rubric approval.'}
    (output / 'SOURCE_MANIFEST.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({'passed': True, 'files': len(contents) + 1, 'archive_created': False,
                      'submission_ready': False}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
