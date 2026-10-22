"""Derived evidence must expose failed judgments and actual operation receipts."""
from copy import deepcopy
import importlib
import json
import hashlib
import sys
from pathlib import Path

import pytest


@pytest.fixture
def builder(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[2] / 'scripts'))
    return importlib.import_module('build_submission_evidence')


def result(answer='A supported answer.'):
    return {'response': {'answer': answer, 'why': ['VERIFIED'], 'citations': [{'source_id': 'doc:policy', 'record_version': 'v1'}],
                         'next_steps': ['Ask for review.'], 'intents_addressed': ['shipping_policy'], 'outcome_claimed': 'ANSWERED'},
            'outcome': 'ANSWERED', 'memory': {'reset': True, 'resolved_reference': True},
            'style': {'verbosity': 'concise', 'version': 2}, 'errors': ['POLICY_TIMEOUT'],
            'tool_records': [{'name': 'get_tracking_events', 'status': 'error', 'error': 'TIMEOUT',
                              'data': None, 'evidence_refs': [], 'duration_ms': 60000}],
            'results': [{'summary': 'Internal agent plan is excluded.'}],
            'raw_outputs': ['Raw attempt is excluded.']}


def judgment(builder, actual, status='measured'):
    metrics = [{'name': name, 'status': 'measured', 'score': .4, 'pass': False, 'reason': 'Unsupported detail.'}
               for name in builder.METRICS]
    if status != 'measured':
        metrics[0] = {'name': 'faithfulness', 'status': status, 'score': None, 'pass': None}
    return {'case_id': 'X', 'evaluated_result_sha256': builder.result_digest(actual), 'metrics': metrics, 'rubric': 'fixed-v1'}


def test_judge_errors_and_missing_context_remain_distinct_and_never_pass(builder):
    actual = result()
    for status, count_key in [('judge_failed', 'judge_failed_case_ids'), ('skipped_no_context', 'no_context_case_ids')]:
        original = judgment(builder, actual, status)
        projected = builder.project_judgments([original], {'X': actual})
        assert projected['X']['metrics'][0]['status'] == status
        assert projected['X']['metrics'][0]['score'] is None
        assert projected['X']['metrics'][0]['pass'] is None
        counts = builder.metric_counts(projected)['faithfulness']
        assert counts[count_key] == ['X']
        assert counts['measured'] == counts['above_threshold'] == 0
        assert counts['mean'] is None
    measured = builder.project_judgments([judgment(builder, actual)], {'X': actual})
    assert builder.metric_counts(measured)['faithfulness']['below_threshold_case_ids'] == ['X']
    assert measured['X']['metrics'][0]['reason'] == 'Unsupported detail.'


@pytest.mark.parametrize('mutation,category', [
    ('missing_case', 'COMPLETE_JUDGE_CASE'), ('missing_metric', 'COMPLETE_JUDGE_METRIC'),
    ('pending_status', 'INCOMPLETE_JUDGE_STATUS'), ('failed_pass', 'UNAVAILABLE_JUDGMENT'),
    ('changed_result', 'JUDGE_RESULT_IDENTITY'), ('inverted_measured_pass', 'INVALID_MEASURED')])
def test_incomplete_or_misbound_judgments_fail_closed(builder, mutation, category):
    actual = result(); row = judgment(builder, actual)
    rows = [row]
    if mutation == 'missing_case': rows = []
    elif mutation == 'missing_metric': row['metrics'].pop()
    elif mutation == 'pending_status': row['metrics'][0]['status'] = 'pending'
    elif mutation == 'failed_pass': row['metrics'][0].update(status='judge_failed', score=None, **{'pass': True})
    elif mutation == 'changed_result': actual['response']['answer'] = 'Changed output.'
    elif mutation == 'inverted_measured_pass': row['metrics'][0]['pass'] = True
    with pytest.raises(ValueError, match=category):
        builder.project_judgments(rows, {'X': actual})


def test_case_projection_preserves_failure_answers_and_receipts_without_raw_plans(builder):
    actual = result()
    row = {'case_id': 'X', 'repeat': 0, 'input_sha256': 'a' * 64,
           'result': actual, 'setup_results': [deepcopy(actual)],
           'feedback': [{'signal': 'too_long', 'type': 'explicit'}],
           'assessment': {'checks': [{'name': 'citation_required', 'passed': False}],
                          'hard_gate_passed': True, 'case_checks_passed': False}}
    saved = deepcopy(row)
    projected = builder.project_cases([row], ['X'])[0]
    assert projected['result']['response'] == actual['response']
    assert projected['result']['tool_records'][0]['error'] == 'TIMEOUT'
    assert projected['setup_results'][0]['response'] == actual['response']
    assert projected['feedback'] == row['feedback']
    assert projected['assessment'] == row['assessment']
    assert 'results' not in projected['result'] and 'raw_outputs' not in projected['result']
    assert row == saved
    with pytest.raises(ValueError, match='CASE_COVERAGE'):
        builder.project_cases([row], ['X'], repeats=3)


def demo_fixture():
    results = {ident: result() for ident in ['N01', 'S04', 'S01']}
    manifest = {'build_sha256': {'src/app.py': 'a' * 64}, 'model_config_sha256': 'b' * 64}
    scenarios = [{'scenario': name, 'case_id': ident, 'origin': 'unchanged_frozen_output', 'passed': True,
                  'result': deepcopy(results[ident])} for name, ident in
                 [('grounded_eligibility', 'N01'), ('prompt_disclosure_refusal', 'S04'), ('injury_mock_escalation', 'S01')]]
    for name, count in [('memory_followup_reset', 4), ('feedback_adaptation_rollback', 9)]:
        scenario = {'scenario': name, 'origin': 'fresh_live_replay', 'passed': False,
                    'checks': {'actual_check': False},
                    'turns': [{'input': '/reset' if i == 2 else 'Synthetic question.', 'result': result()} for i in range(count)]}
        if count == 9:
            scenario.update(feedback=[{'signal': 'too_long', 'type': 'explicit'}],
                            observed_answer_words={'before': 3, 'after': 3, 'rollback': 3},
                            identical_citation_sections_observed=True)
        scenarios.append(scenario)
    demo = {'build_sha256': manifest['build_sha256'], 'model_config_sha256': manifest['model_config_sha256'],
            'source_outputs_sha256': 'c' * 64, 'scenarios': scenarios, 'passed': False}
    return demo, manifest, results


def test_demo_keeps_failed_checks_actual_turns_feedback_versions_and_word_counts(builder):
    demo, manifest, results = demo_fixture(); saved = deepcopy(demo)
    projected = builder.project_demo(demo, manifest, 'c' * 64, results)
    assert projected['passed'] is False
    assert len(projected['scenarios']) == 5
    adaptation = projected['scenarios'][-1]
    assert adaptation['origin'] == 'fresh_live_replay' and adaptation['passed'] is False
    assert len(adaptation['turns']) == 9
    assert adaptation['turns'][2]['input'] == '/reset'
    assert adaptation['turns'][1]['result']['response'] == result()['response']
    assert adaptation['turns'][1]['result']['style']['version'] == 2
    assert adaptation['turns'][2]['result']['memory']['reset'] is True
    assert adaptation['feedback'] == demo['scenarios'][-1]['feedback']
    assert adaptation['observed_answer_words'] == {'before': 3, 'after': 3, 'rollback': 3}
    assert demo == saved


@pytest.mark.parametrize('mutation', ['output_hash', 'missing_scenario', 'reused_prose', 'missing_turn', 'invented_count'])
def test_incomplete_or_altered_demo_is_not_accepted(builder, mutation):
    demo, manifest, results = demo_fixture()
    if mutation == 'output_hash': demo['source_outputs_sha256'] = 'd' * 64
    elif mutation == 'missing_scenario': demo['scenarios'].pop()
    elif mutation == 'reused_prose': demo['scenarios'][0]['result']['response']['answer'] = 'Another run.'
    elif mutation == 'missing_turn': demo['scenarios'][-1]['turns'].pop()
    elif mutation == 'invented_count': demo['scenarios'][-1]['observed_answer_words']['after'] = 1
    with pytest.raises(ValueError):
        builder.project_demo(demo, manifest, 'c' * 64, results)


def test_neutral_projection_minimizes_identifiers_and_keeps_digest_bytes(builder):
    projected = builder.neutral_projection({'answer': 'Synthetic deployment-id says order O-1001.',
                                            'digest': '1234567890abcdef' * 4}, [('deployment-id', '[application_model]')])
    assert 'deployment-id' not in projected['answer'] and 'O-1001' not in projected['answer']
    assert '[application_model]' in projected['answer']
    assert projected['digest'] == '1234567890abcdef' * 4


def test_configured_credentials_are_removed_before_digest_shaped_customer_text(builder):
    secret = 'd' * 64
    normal_hash = '1234567890abcdef' * 4
    projected = builder.neutral_projection({'answer': secret,
        'next_steps': ['The configured value is ' + secret + '.'], 'source_sha256': normal_hash}, secrets=(secret,))
    assert secret not in json.dumps(projected)
    assert projected['answer'] == '[REDACTED-SECRET]'
    assert projected['source_sha256'] == normal_hash
    assert '[REDACTED-SECRET]' in projected['next_steps'][0]
    with pytest.raises(ValueError, match='CREDENTIAL_COLLIDES_WITH_PROVENANCE'):
        builder.neutral_projection({'original_artifact_sha256': {'receipt': secret}}, secrets=(secret,))
    with pytest.raises(ValueError, match='CREDENTIAL_COLLIDES_WITH_PROVENANCE'):
        builder.neutral_projection({'source_sha256': normal_hash}, secrets=('1234567890abcdef',))
    with pytest.raises(ValueError, match='CREDENTIAL_COLLIDES_WITH_PROVENANCE'):
        builder.neutral_projection({'tool_records': [{'data': {'packet_hash': secret}}]}, secrets=(secret,))


def test_complete_builder_preserves_case_judgment_review_and_demo_evidence(builder, tmp_path, monkeypatch):
    """Exercise the file joins using synthetic receipts, with no endpoint/config reads."""
    from independent_review_gate import agreement
    ids = ['N01', 'S04', 'S01'] + [f'X{i:02}' for i in range(62)]
    functional_dir, safety_dir, output = [tmp_path / name for name in ('full', 'safety', 'derived')]
    def write(path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value))
    def jsonl(path, rows):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(''.join(json.dumps(row) + '\n' for row in rows))
    write(tmp_path / 'data/evaluation_cases.json', {'cases': [{'id': ident, 'input': 'Synthetic question.'} for ident in ids]})
    protocol = {'consistency_ids': ids[:15], 'human_review_ids': ids[:20]}
    write(tmp_path / 'evaluation/phase9/protocol_v1.json', protocol)
    manifest = {'build_sha256': {'src/app.py': 'a' * 64}, 'model_config_sha256': 'b' * 64,
                'context_sha256': 'c' * 64, 'dataset_sha256': builder.digest(tmp_path / 'data/evaluation_cases.json'),
                'protocol_sha256': builder.digest(tmp_path / 'evaluation/phase9/protocol_v1.json'),
                'case_ids': ids, 'model_settings': {'model': 'synthetic-application'}}
    def case(ident, repeat=0):
        return {'case_id': ident, 'repeat': repeat, 'result': result(), 'setup_results': [], 'feedback': [],
                'assessment': {'checks': [{'name': 'required_evidence', 'passed': False}],
                               'hard_gate_passed': True, 'case_checks_passed': False,
                               'original_action_flow_criterion': 'in_scope'}}
    main_rows = [case(ident) for ident in ids]
    safety_rows = [case(ident, repeat) for ident in ids[:15] for repeat in range(3)]
    for directory, rows, selection in [(functional_dir, main_rows, ids), (safety_dir, safety_rows, ids[:15])]:
        write(directory / 'manifest.json', manifest | {'case_ids': selection})
        jsonl(directory / 'outputs.jsonl', rows)
        failures = [{'case_id': row['case_id'], 'repeat': row['repeat'], 'outcome': row['result']['outcome'],
                     'failed_checks': ['required_evidence']} for row in rows]
        write(directory / 'summary.json', {'runs': len(rows), 'hard_gate_case_passes': len(rows),
                                         'all_case_check_passes': 0, 'scope_exclusions': 0, 'case_failures': failures})
        write(directory / 'ticket_readback.json', {'passed': True, 'handoffs_checked': 0, 'checks': []})
    write(safety_dir / 'consistency.json', {'complete': True, 'runs': 45, 'details': [{'case_id': ids[0], 'failed_checks': ['required_evidence']}]})
    output_hash = builder.digest(functional_dir / 'outputs.jsonl')
    judge_rows = []
    for row in main_rows:
        j = judgment(builder, row['result'], 'skipped_no_context'); j['case_id'] = row['case_id']; judge_rows.append(j)
    for path in [functional_dir, functional_dir / 'judges/second']:
        jsonl(path / 'judgments_all.jsonl', judge_rows)
        write(path / 'judge_all_manifest.json', {'source_outputs_sha256': output_hash, 'judged_cases': 65,
                                               'requested_cases': 65, 'judge_settings': {'model': 'synthetic-judge'}})
    comparison = builder.paired_scores(judge_rows, judge_rows, ids)
    comparison.update(source_outputs_sha256=output_hash, different_model_ids=False)
    write(functional_dir / 'judge_comparison_second.json', comparison)
    packet = b'Exact synthetic review packet.'
    (functional_dir / 'human_review.md').write_bytes(packet)
    packet_hash = hashlib.sha256(packet).hexdigest()
    review = {'status': 'reviewed_by_independent_ai', 'reviewer_type': 'ai_proxy', 'review_packet_sha256': packet_hash,
              'cases': [{'case_id': ident, 'faithfulness': None, 'answer_relevancy': 1., 'grounded_support': 1.,
                         'not_applicable_metrics': {'faithfulness': 'No tool context.'},
                         'unsafe_or_unsupported_claim': False, 'comment': 'Specific review observation.'} for ident in ids[:20]],
              'issues': [{'case_id': 'N01', 'severity': 'minor', 'evidence': 'A retained minor observation.'}]}
    write(functional_dir / 'independent_ai_review.json', review)
    write(functional_dir / 'independent_ai_agreement.json', agreement(judge_rows[:20], review, packet, ids[:20]))
    write(functional_dir / 'review_packet_manifest.json', {'source_outputs_sha256': output_hash,
        'build_sha256': manifest['build_sha256'], 'review_packet_sha256': packet_hash})
    demo, _, _ = demo_fixture()
    demo.update(build_sha256=manifest['build_sha256'], model_config_sha256=manifest['model_config_sha256'], source_outputs_sha256=output_hash)
    for scenario in demo['scenarios'][:3]: scenario['passed'] = False
    demo_path = tmp_path / 'demo.json'; write(demo_path, demo)
    hosted = tmp_path / 'hosted.json'; write(hosted, {'passed': False})
    offline = tmp_path / 'offline.json'; write(offline, {'build_sha256': manifest['build_sha256'],
        'tests_passed': 10, 'elapsed_seconds': 1., 'limits': 'Synthetic offline receipt.'})
    monkeypatch.setattr(builder, 'ROOT', tmp_path)
    monkeypatch.setattr(builder, 'load_environment', lambda _: {})
    monkeypatch.setattr(sys, 'argv', ['builder', '--run-dir', str(functional_dir), '--safety-dir', str(safety_dir),
        '--output-dir', str(output), '--demo', str(demo_path), '--hosted-readback', str(hosted), '--offline-receipt', str(offline)])
    builder.main()
    audit = json.loads((output / 'final_case_evidence.json').read_text())
    assert len(audit['functional_cases']) == 65 and len(audit['safety_cases']) == 45
    assert len(audit['independent_ai_review']['cases']) == 20
    assert audit['independent_ai_review']['issues'][0]['severity'] == 'minor'
    assert audit['functional_cases'][0]['judgments']['second']['metrics'][0]['status'] == 'skipped_no_context'
    assert audit['functional_cases'][0]['independent_ai_review']['comment'] == 'Specific review observation.'
    summary = json.loads((output / 'evaluation_summary.json').read_text())
    assert summary['functional_checks']['all_case_check_passes'] == 0
    assert len(summary['quality_metrics']['faithfulness']['primary']['no_context_case_ids']) == 65
    assert len(summary['quality_metrics']['grounded_support']['second']['below_threshold_case_ids']) == 65
    assert summary['submission_ready'] is False
    assert json.loads((output / 'demo_evidence.json').read_text())['scenarios'][-1]['passed'] is False
    # A stale comparison must fail before producing another derived package.
    comparison['source_outputs_sha256'] = 'd' * 64
    write(functional_dir / 'judge_comparison_second.json', comparison)
    with pytest.raises(ValueError, match='COMPARISON_OUTPUT_IDENTITY'):
        builder.main()
