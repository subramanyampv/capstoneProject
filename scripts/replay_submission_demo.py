"""Record five submission scenarios without changing the frozen application build."""
import argparse
import hashlib
import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from capstone_agent.config import LLMConfig, load_environment
from capstone_agent.evaluation.export import minimized_json, verified_tickets
from capstone_agent.observability.support_tracing import EXPORTER
from capstone_agent.retrieval.chroma_store import PolicySearch
from capstone_agent.retrieval.configured_embeddings import ConfiguredEmbeddings
from capstone_agent.support.memory import SessionMemory
from capstone_agent.support.preferences import PreferenceStore
from capstone_agent.support.registry import SessionIdentity
from capstone_agent.support.runtime import run_support
from run_final_suite import ROOT, build_hashes


def assert_candidate(manifest):
    if build_hashes() != manifest['build_sha256']:
        raise ValueError('DEMO_BUILD_DIFFERS_FROM_FROZEN_RUN')
    config = LLMConfig.from_env(ROOT / '.env')
    fingerprint = hashlib.sha256(json.dumps({'settings': config.public_settings(),
                                            'endpoint': config.base_url}, sort_keys=True).encode()).hexdigest()
    if fingerprint != manifest['model_config_sha256']:
        raise ValueError('DEMO_CONFIGURATION_DIFFERS_FROM_FROZEN_RUN')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run-dir', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads((args.run_dir / 'manifest.json').read_text())
    assert_candidate(manifest)
    rows = {r['case_id']: r for r in map(json.loads, (args.run_dir / 'outputs.jsonl').read_text().splitlines())}
    env = load_environment(ROOT / '.env')
    secrets = tuple(v for k, v in env.items() if k.endswith('API_KEY') and v)
    scenarios = []
    for ident, label in [('N01', 'grounded_eligibility'), ('S04', 'prompt_disclosure_refusal'), ('S01', 'injury_mock_escalation')]:
        row = rows[ident]
        scenarios.append({'scenario': label, 'origin': 'unchanged_frozen_output', 'case_id': ident,
                          'result': row['result'], 'passed': row['assessment']['case_checks_passed']})

    search = PolicySearch(ConfiguredEmbeddings())
    search.search('shipping policy')
    with tempfile.TemporaryDirectory() as isolated:
        preferences = PreferenceStore(Path(isolated))
        memory = SessionMemory()
        identity = SessionIdentity('C-100')
        def turn(query):
            assert_candidate(manifest)
            result = run_support(query, identity=identity, search=search, memory=memory,
                                 preferences=preferences)
            print('demo', result['outcome'], 'model_calls', result['model_calls'], flush=True)
            return {'input': query, 'result': result}
        try:
            turns = [turn('Track order O-1001.'), turn('What about that order?'),
                     turn('/reset'), turn('Track that order.')]
            results = [r['result'] for r in turns]
            checks = {
                'initial_tracking_answered': results[0]['outcome'] == 'ANSWERED',
                'followup_resolves_reference': bool(results[1]['memory'].get('resolved_reference')),
                'followup_reads_fresh_tracking': any(t['name'] == 'get_tracking_events' and t['status'] == 'ok' for t in results[1]['tool_records']),
                'reset_recorded': bool(results[2]['memory'].get('reset')),
                'post_reset_clarifies_without_model': results[3]['outcome'] == 'CLARIFICATION_REQUESTED' and results[3]['model_calls'] == 0,
            }
            scenarios.append({'scenario': 'memory_followup_reset', 'origin': 'fresh_live_replay',
                              'turns': turns, 'checks': checks, 'passed': all(checks.values())})
            turn('/reset')
            query = 'Explain the standard and express shipping estimates, international coverage and delivery guarantees.'
            adaptation = [turn('/feedback enable'), turn(query), turn('/feedback too_long'),
                          turn('/feedback too_long'), turn('/reset'), turn(query),
                          turn('/feedback reset_style'), turn('/reset'), turn(query)]
            before, after, rollback = [adaptation[i]['result'] for i in (1, 5, 8)]
            feedback_path = Path(isolated) / 'data/runtime/feedback.jsonl'
            feedback = [json.loads(s) for s in feedback_path.read_text().splitlines()]
            citations = lambda r: {json.dumps(c, sort_keys=True) for c in r['response']['citations']}
            document_scopes = lambda r: {(c['source_id'], c['record_version']) for c in r['response']['citations'] if c['source_id'].startswith('doc:')}
            checks = {
                'all_policy_answers_completed': all(r['outcome'] == 'ANSWERED' for r in (before, after, rollback)),
                'two_explicit_signals_saved': sum(r['signal'] == 'too_long' and r['type'] == 'explicit' for r in feedback) == 2,
                'standard_before': before['style']['verbosity'] == 'standard',
                'concise_after': after['style']['verbosity'] == 'concise',
                'standard_after_rollback': rollback['style']['verbosity'] == 'standard',
                'same_policy_document_versions': bool(document_scopes(before)) and document_scopes(before) == document_scopes(after) == document_scopes(rollback),
                'shorter_answer_observed': len(after['response']['answer'].split()) < len(before['response']['answer'].split()),
            }
            scenarios.append({'scenario': 'feedback_adaptation_rollback', 'origin': 'fresh_live_replay',
                              'turns': adaptation, 'feedback': feedback, 'checks': checks,
                              'identical_citation_sections_observed': citations(before) == citations(after) == citations(rollback),
                              'observed_answer_words': {k: len(v['response']['answer'].split()) for k, v in [('before', before), ('after', after), ('rollback', rollback)]},
                              'passed': all(checks.values())})
        finally:
            memory.close()
    EXPORTER.wait(10)
    tickets = []
    for scenario in scenarios:
        for result in ([scenario['result']] if 'result' in scenario else [t['result'] for t in scenario['turns']]):
            tickets.extend(verified_tickets(result))
    report = {'recorded_at': datetime.now(timezone.utc).isoformat(),
              'source_outputs_sha256': hashlib.sha256((args.run_dir / 'outputs.jsonl').read_bytes()).hexdigest(),
              'build_sha256': manifest['build_sha256'],
              'model_config_sha256': manifest['model_config_sha256'], 'scenarios': scenarios,
              'passed': all(s['passed'] for s in scenarios),
              'limits': 'Three scenarios reuse identified frozen outputs; two are fresh live multi-turn replays on the same build. Synthetic users and local mock handoffs only. Observed word counts are one replay, not a causal quality or performance claim.'}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    exported = json.loads(minimized_json(report, secrets, verified_ticket_ids=tuple(tickets)))
    # These are computed source digests, not request content. Restore exact bytes
    # only after checking credential redaction still takes precedence.
    identity_wire = json.dumps({'build_sha256': report['build_sha256'],
                                'source_outputs_sha256': report['source_outputs_sha256']})
    if any(secret in identity_wire for secret in secrets):
        raise ValueError('CREDENTIAL_COLLIDES_WITH_BUILD_IDENTITY')
    exported['build_sha256'] = report['build_sha256']
    exported['source_outputs_sha256'] = report['source_outputs_sha256']
    if any(secret in report['model_config_sha256'] for secret in secrets):
        raise ValueError('CREDENTIAL_COLLIDES_WITH_CONFIGURATION_IDENTITY')
    exported['model_config_sha256'] = report['model_config_sha256']
    args.output.write_text(json.dumps(exported, indent=2, allow_nan=False) + '\n')
    print(json.dumps({'passed': report['passed'], 'scenarios': [{'scenario': s['scenario'], 'passed': s['passed'], 'checks': s.get('checks', {})} for s in scenarios]}, indent=2))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
