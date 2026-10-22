"""Derive role-neutral evidence summaries; preserve original experiment bytes."""
import argparse
import hashlib
import json
import math
import re
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from capstone_agent.evaluation.calibration import METRICS
from capstone_agent.config import load_environment
from capstone_agent.support.privacy import minimize
from capstone_agent.evaluation.export import verified_tickets
from compare_judges import paired_scores
from independent_review_gate import validate_review

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def result_digest(result):
    return hashlib.sha256(json.dumps(result, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def exact_rows(rows, expected_ids, repeats=1):
    expected = {(ident, repeat) for ident in expected_ids for repeat in range(repeats)}
    actual = [(row.get('case_id'), row.get('repeat')) for row in rows]
    if len(actual) != len(set(actual)) or set(actual) != expected:
        raise ValueError('INCOMPLETE_OR_DUPLICATE_CASE_COVERAGE')


def project_result(result):
    """Customer prose and operation receipts; never raw attempts or agent plans."""
    if not isinstance(result.get('response'), dict) or not isinstance(result.get('outcome'), str):
        raise ValueError('COMPLETE_CUSTOMER_RESPONSE_REQUIRED')
    names = ('response', 'outcome', 'ticket', 'refusals', 'triggers', 'obligation_contract',
             'obligation_audit', 'answer_fallback', 'bounded_claim_repair', 'errors', 'memory',
             'style', 'model_calls', 'tool_calls', 'handoffs', 'replans', 'repairs', 'tokens',
             'safety_version', 'latency_ms')
    projected = {name: deepcopy(result[name]) for name in names if name in result}
    projected['original_result_sha256'] = result_digest(result)
    projected['tool_records'] = [{key: deepcopy(tool[key]) for key in
        ('name', 'status', 'data', 'error', 'evidence_refs', 'duration_ms') if key in tool}
        for tool in result.get('tool_records', [])]
    return projected


def project_cases(rows, expected_ids, repeats=1):
    exact_rows(rows, expected_ids, repeats)
    projected = []
    for row in rows:
        assessment = row.get('assessment', {})
        if not isinstance(assessment.get('checks'), list) or any(
            type(assessment.get(key)) is not bool for key in ('hard_gate_passed', 'case_checks_passed')):
            raise ValueError('COMPLETE_CASE_ASSESSMENT_REQUIRED')
        if any(type(check.get('passed')) is not bool for check in assessment['checks']):
            raise ValueError('EXPLICIT_CHECK_RESULT_REQUIRED')
        projected.append({key: deepcopy(row[key]) for key in
            ('case_id', 'repeat', 'category', 'input_sha256', 'assessment', 'feedback', 'case_elapsed_ms')
            if key in row} | {'result': project_result(row['result']),
                             'setup_results': [project_result(r) for r in row.get('setup_results', [])]})
    return projected


def project_judgments(rows, results):
    """An explicit judge failure is an error, distinct from inapplicable context."""
    ids = [row.get('case_id') for row in rows]
    if len(ids) != len(set(ids)) or set(ids) != set(results):
        raise ValueError('COMPLETE_JUDGE_CASE_COVERAGE_REQUIRED')
    projected = {}
    for row in rows:
        expected_hash = result_digest(results[row['case_id']])
        if row.get('evaluated_result_sha256') != expected_hash:
            raise ValueError('JUDGE_RESULT_IDENTITY_MISMATCH')
        metrics = row.get('metrics', [])
        if len(metrics) != len(METRICS) or {m.get('name') for m in metrics} != set(METRICS):
            raise ValueError('COMPLETE_JUDGE_METRIC_STATUSES_REQUIRED')
        for metric in metrics:
            status, score, passed = metric.get('status'), metric.get('score'), metric.get('pass')
            if status == 'measured':
                if (type(score) not in (int, float) or not math.isfinite(score) or not 0 <= score <= 1
                        or type(passed) is not bool or passed != (score >= METRICS[metric['name']])):
                    raise ValueError('INVALID_MEASURED_JUDGMENT')
            elif status in {'skipped_no_context', 'judge_failed'}:
                if score is not None or passed is not None or 'score' not in metric or 'pass' not in metric:
                    raise ValueError('UNAVAILABLE_JUDGMENT_CANNOT_PASS')
                if status == 'skipped_no_context' and metric['name'] != 'faithfulness':
                    raise ValueError('INVALID_NO_CONTEXT_METRIC')
            else:
                raise ValueError('INCOMPLETE_JUDGE_STATUS')
        projected[row['case_id']] = {'case_id': row['case_id'], 'rubric': row.get('rubric'),
            'evaluated_result_sha256': expected_hash,
            'metrics': [{key: deepcopy(m[key]) for key in ('name', 'score', 'pass', 'status', 'reason')
                         if key in m} for m in metrics]}
    return projected


def metric_counts(judgments):
    report = {}
    for name, threshold in METRICS.items():
        metrics = [(ident, next(m for m in row['metrics'] if m['name'] == name))
                   for ident, row in judgments.items()]
        measured = [(ident, m) for ident, m in metrics if m['status'] == 'measured']
        report[name] = {'threshold': threshold, 'total': len(metrics), 'measured': len(measured),
            'mean': sum(m['score'] for _, m in measured) / len(measured) if measured else None,
            'above_threshold': sum(m['pass'] for _, m in measured),
            'below_threshold_case_ids': [ident for ident, m in measured if not m['pass']],
            'no_context_case_ids': [ident for ident, m in metrics if m['status'] == 'skipped_no_context'],
            'judge_failed_case_ids': [ident for ident, m in metrics if m['status'] == 'judge_failed']}
    return report


def project_demo(demo, manifest, output_hash, results):
    if (demo.get('build_sha256') != manifest['build_sha256'] or
            demo.get('model_config_sha256') != manifest['model_config_sha256'] or
            demo.get('source_outputs_sha256') != output_hash):
        raise ValueError('DEMO_SOURCE_OR_CONFIGURATION_MISMATCH')
    required = {'grounded_eligibility': 'N01', 'prompt_disclosure_refusal': 'S04',
                'injury_mock_escalation': 'S01', 'memory_followup_reset': None,
                'feedback_adaptation_rollback': None}
    scenarios = demo.get('scenarios', [])
    names = [s.get('scenario') for s in scenarios]
    if len(names) != len(set(names)) or set(names) != set(required):
        raise ValueError('EXACT_FIVE_DEMO_SCENARIOS_REQUIRED')
    if type(demo.get('passed')) is not bool or demo['passed'] != all(s.get('passed') is True for s in scenarios):
        raise ValueError('INVALID_DEMO_AGGREGATE')
    projected = []
    for scenario in scenarios:
        if type(scenario.get('passed')) is not bool:
            raise ValueError('EXPLICIT_DEMO_RESULT_REQUIRED')
        item = {key: deepcopy(scenario[key]) for key in ('scenario', 'origin', 'case_id', 'passed', 'checks',
            'feedback', 'identical_citation_sections_observed', 'observed_answer_words') if key in scenario}
        ident = required[scenario['scenario']]
        if ident:
            if (scenario.get('origin') != 'unchanged_frozen_output' or scenario.get('case_id') != ident
                    or scenario.get('result') != results.get(ident)):
                raise ValueError('DEMO_REUSED_OUTPUT_MISMATCH')
            item['result'] = project_result(scenario['result'])
        else:
            turns = scenario.get('turns', [])
            count = 4 if scenario['scenario'] == 'memory_followup_reset' else 9
            if (scenario.get('origin') != 'fresh_live_replay' or len(turns) != count
                    or not isinstance(scenario.get('checks'), dict) or not scenario['checks']
                    or any(type(v) is not bool for v in scenario['checks'].values())
                    or scenario['passed'] != all(scenario['checks'].values())):
                raise ValueError('COMPLETE_FRESH_DEMO_RECEIPTS_REQUIRED')
            if scenario['scenario'] == 'feedback_adaptation_rollback' and (
                not isinstance(scenario.get('feedback'), list) or not scenario.get('observed_answer_words')):
                raise ValueError('ADAPTATION_FEEDBACK_AND_WORD_COUNTS_REQUIRED')
            if scenario['scenario'] == 'feedback_adaptation_rollback':
                observed = {name: len(turns[index]['result']['response']['answer'].split())
                            for name, index in (('before', 1), ('after', 5), ('rollback', 8))}
                if observed != scenario['observed_answer_words']:
                    raise ValueError('DEMO_WORD_COUNTS_DO_NOT_MATCH_ACTUAL_ANSWERS')
            item['turns'] = [{'input': turn['input'], 'result': project_result(turn['result'])} for turn in turns]
        projected.append(item)
    return {'recorded_at': demo.get('recorded_at'), 'source_outputs_sha256': output_hash,
            'application_configuration_digest': manifest['model_config_sha256'],
            'candidate_build_digest': hashlib.sha256(json.dumps(manifest['build_sha256'], sort_keys=True).encode()).hexdigest(),
            'scenarios': projected, 'passed': demo['passed'], 'limits': demo.get('limits')}


def neutral_projection(value, identity_replacements=(), verified_ticket_ids=(), *, secrets=(), _provenance=False):
    """Re-minimize selected content while retaining validated digest bytes."""
    if isinstance(value, dict):
        return {key: neutral_projection(part, identity_replacements, verified_ticket_ids, secrets=secrets,
            _provenance=_provenance or key in {'sha256', 'digest', 'hash'} or key.endswith(('_sha256', '_digest', '_hash')))
            for key, part in value.items()}
    if isinstance(value, list):
        return [neutral_projection(part, identity_replacements, verified_ticket_ids,
                                   secrets=secrets, _provenance=_provenance) for part in value]
    if isinstance(value, str):
        # A customer string that resembles a digest has no credential exemption.
        # Actual provenance must retain its bytes, so a collision blocks export.
        for secret in secrets:
            if secret and secret in value:
                if _provenance:
                    raise ValueError('CREDENTIAL_COLLIDES_WITH_PROVENANCE')
                value = value.replace(secret, '[REDACTED-SECRET]')
        if re.fullmatch('[a-f0-9]{64}', value):
            return value
        for private, alias in sorted(identity_replacements, key=lambda p: -len(p[0])):
            if private:
                value = value.replace(private, alias)
        return minimize(value, secrets, verified_ticket_ids=verified_ticket_ids)
    return value


def check_summary(summary, rows):
    actual = {'runs': len(rows),
              'hard_gate_case_passes': sum(r['assessment']['hard_gate_passed'] for r in rows),
              'all_case_check_passes': sum(r['assessment']['case_checks_passed'] for r in rows)}
    actual['scope_exclusions'] = sum(r['assessment'].get('original_action_flow_criterion') == 'outside_v3_scope' for r in rows)
    actual['case_failures'] = [{'case_id': r['case_id'], 'repeat': r['repeat'], 'outcome': r['result']['outcome'],
        'failed_checks': [c['name'] for c in r['assessment']['checks'] if not c['passed']]}
        for r in rows if not r['assessment']['case_checks_passed']]
    if any(summary.get(key) != value for key, value in actual.items()):
        raise ValueError('SUMMARY_DOES_NOT_MATCH_CASE_ROWS')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run-dir', type=Path, required=True)
    parser.add_argument('--safety-dir', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--demo', type=Path, required=True)
    parser.add_argument('--hosted-readback', type=Path, required=True)
    parser.add_argument('--offline-receipt', type=Path, required=True)
    args = parser.parse_args()
    read = lambda path: json.loads(path.read_text())
    main_manifest = read(args.run_dir / 'manifest.json')
    safety_manifest = read(args.safety_dir / 'manifest.json')
    for key in ('build_sha256', 'model_config_sha256', 'context_sha256', 'dataset_sha256', 'protocol_sha256'):
        if main_manifest[key] != safety_manifest[key]:
            raise ValueError('CANDIDATE_IDENTITY_MISMATCH')
    original_paths = {
        'functional_run': args.run_dir / 'summary.json',
        'functional_outputs': args.run_dir / 'outputs.jsonl',
        'primary_judgments': args.run_dir / 'judgments_all.jsonl',
        'primary_judge_manifest': args.run_dir / 'judge_all_manifest.json',
        'second_judgments': args.run_dir / 'judges/second/judgments_all.jsonl',
        'second_judge_manifest': args.run_dir / 'judges/second/judge_all_manifest.json',
        'independent_ai_review': args.run_dir / 'independent_ai_review.json',
        'review_packet': args.run_dir / 'human_review.md',
        'review_packet_manifest': args.run_dir / 'review_packet_manifest.json',
        'functional_manifest': args.run_dir / 'manifest.json',
        'functional_ticket_readback': args.run_dir / 'ticket_readback.json',
        'quality_comparison': args.run_dir / 'judge_comparison_second.json',
        'independent_ai_review_gate': args.run_dir / 'independent_ai_agreement.json',
        'safety_summary': args.safety_dir / 'summary.json',
        'safety_outputs': args.safety_dir / 'outputs.jsonl',
        'safety_manifest': args.safety_dir / 'manifest.json',
        'safety_consistency': args.safety_dir / 'consistency.json',
        'safety_ticket_readback': args.safety_dir / 'ticket_readback.json',
        'final_hosted_trace_readback': args.hosted_readback,
        'current_demo': args.demo,
        'offline_validation': args.offline_receipt,
    }
    missing = [name for name, path in original_paths.items() if not path.is_file()]
    if missing:
        raise ValueError('MISSING_FINAL_EVIDENCE: ' + ','.join(missing))
    functional = read(original_paths['functional_run'])
    safety = read(original_paths['safety_summary'])
    consistency = read(original_paths['safety_consistency'])
    comparison = read(original_paths['quality_comparison'])
    review = read(original_paths['independent_ai_review_gate'])
    demo = read(original_paths['current_demo'])
    offline = read(original_paths['offline_validation'])
    build_digest = hashlib.sha256(json.dumps(main_manifest['build_sha256'], sort_keys=True).encode()).hexdigest()
    if demo['build_sha256'] != main_manifest['build_sha256']:
        raise ValueError('DEMO_IDENTITY_MISMATCH')
    if demo['model_config_sha256'] != main_manifest['model_config_sha256']:
        raise ValueError('DEMO_CONFIGURATION_MISMATCH')
    if offline['build_sha256'] != main_manifest['build_sha256']:
        raise ValueError('OFFLINE_IDENTITY_MISMATCH')
    rows = lambda path: [json.loads(line) for line in path.read_text().splitlines()]
    protocol = read(ROOT / 'evaluation/phase9/protocol_v1.json')
    expected = [case['id'] for case in read(ROOT / 'data/evaluation_cases.json')['cases']]
    if len(expected) != 65 or set(main_manifest['case_ids']) != set(expected):
        raise ValueError('COMPLETE_PUBLIC_FROZEN_SET_REQUIRED')
    if digest(ROOT / 'data/evaluation_cases.json') != main_manifest['dataset_sha256']:
        raise ValueError('PUBLIC_DATASET_IDENTITY_MISMATCH')
    if digest(ROOT / 'evaluation/phase9/protocol_v1.json') != main_manifest['protocol_sha256']:
        raise ValueError('PUBLIC_PROTOCOL_IDENTITY_MISMATCH')
    raw_functional = rows(original_paths['functional_outputs'])
    raw_safety = rows(original_paths['safety_outputs'])
    functional_cases = project_cases(raw_functional, expected)
    if len(protocol['consistency_ids']) != 15 or set(safety_manifest['case_ids']) != set(protocol['consistency_ids']):
        raise ValueError('EXACT_SAFETY_SET_REQUIRED')
    safety_cases = project_cases(raw_safety, protocol['consistency_ids'], 3)
    check_summary(functional, raw_functional)
    check_summary(safety, raw_safety)
    if consistency.get('complete') is not True or consistency.get('runs') != 45:
        raise ValueError('COMPLETE_SAFETY_CONSISTENCY_REQUIRED')
    results = {row['case_id']: row['result'] for row in raw_functional}
    output_hash = digest(original_paths['functional_outputs'])
    primary_manifest = read(original_paths['primary_judge_manifest'])
    second_manifest = read(original_paths['second_judge_manifest'])
    for manifest in (primary_manifest, second_manifest):
        if (manifest.get('source_outputs_sha256') != output_hash or manifest.get('judged_cases') != 65
                or manifest.get('requested_cases') != 65):
            raise ValueError('COMPLETE_OUTPUT_BOUND_JUDGE_MANIFEST_REQUIRED')
    if comparison.get('source_outputs_sha256') != output_hash or comparison.get('complete_case_coverage') is not True:
        raise ValueError('COMPARISON_OUTPUT_IDENTITY_OR_COVERAGE_MISMATCH')
    primary = project_judgments(rows(original_paths['primary_judgments']), results)
    second = project_judgments(rows(original_paths['second_judgments']), results)
    paired = paired_scores(list(primary.values()), list(second.values()), list(results))
    if paired['metrics'] != comparison['metrics']:
        raise ValueError('COMPARISON_DOES_NOT_MATCH_JUDGE_ROWS')
    metrics = {name: {'threshold': METRICS[name],
                     'paired_measurements': paired['metrics'][name]['paired_measurements'],
                     'pass_fail_agreement': paired['metrics'][name]['pass_fail_agreement'],
                     'primary': metric_counts(primary)[name], 'second': metric_counts(second)[name]}
               for name in METRICS}
    raw_review = read(original_paths['independent_ai_review'])
    if len(protocol['human_review_ids']) != 20:
        raise ValueError('EXACT_TWENTY_CASE_REVIEW_REQUIRED')
    checked_review = validate_review(raw_review, original_paths['review_packet'].read_bytes(), protocol['human_review_ids'])
    packet_manifest = read(original_paths['review_packet_manifest'])
    if (packet_manifest.get('source_outputs_sha256') != output_hash or
            packet_manifest.get('build_sha256') != main_manifest['build_sha256'] or
            packet_manifest.get('review_packet_sha256') != checked_review['review_packet_sha256']):
        raise ValueError('REVIEW_PACKET_SOURCE_IDENTITY_MISMATCH')
    if any(review.get(key) != checked_review[key] for key in
           ('status', 'reviewer_type', 'reviewed_cases', 'unsafe_case_ids', 'blocking_issues', 'review_packet_sha256')):
        raise ValueError('REVIEW_GATE_DOES_NOT_MATCH_ACTUAL_REVIEW')
    review_by_case = {row['case_id']: row for row in raw_review['cases']}
    for row in functional_cases:
        ident = row['case_id']
        row['judgments'] = {'primary': primary[ident], 'second': second[ident]}
        row['independent_ai_review'] = deepcopy(review_by_case.get(ident))
    demo_evidence = project_demo(demo, main_manifest, output_hash, results)
    assessments = {r['case_id']: r['assessment'] for r in raw_functional}
    if any(s['passed'] != assessments[s['case_id']]['case_checks_passed'] for s in demo['scenarios'] if 'case_id' in s):
        raise ValueError('REUSED_DEMO_ASSESSMENT_MISMATCH')
    provenance = {role: digest(path) for role, path in original_paths.items()}
    case_evidence = {'candidate_build_digest': build_digest,
        'application_configuration_digest': main_manifest['model_config_sha256'],
        'source_outputs_sha256': output_hash, 'functional_cases': functional_cases,
        'safety_cases': safety_cases, 'safety_consistency': consistency,
        'independent_ai_review': {key: deepcopy(raw_review[key]) for key in
            ('status', 'reviewer_type', 'review_packet_sha256', 'cases', 'issues')},
        'quality_disagreements': paired['disagreements'],
        'ticket_readback': {role: read(original_paths[role]) for role in
            ('functional_ticket_readback', 'safety_ticket_readback')},
        'judge_configuration_digests': {role: hashlib.sha256(json.dumps(manifest['judge_settings'], sort_keys=True).encode()).hexdigest()
            for role, manifest in (('primary', primary_manifest), ('second', second_manifest))},
        'original_artifact_sha256': provenance,
        'limits': 'Derived customer-visible responses and verified operation receipts; raw model attempts and internal plans excluded. Judge failure and no-context statuses remain distinct. AI review is not actual human calibration. Original artifacts remain private and unchanged.'}
    report = {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'presentation': 'Derived neutral summary. Application, primary judge and second judge are role aliases. Original identities, artifacts and all earlier failures are preserved privately.',
        'candidate_build_digest': build_digest,
        'application_configuration_digest': main_manifest['model_config_sha256'],
        'offline_tests': {'passed': offline['tests_passed'], 'elapsed_seconds': offline['elapsed_seconds'],
                          'limits': offline['limits']},
        'functional_checks': {key: functional[key] for key in ('runs', 'hard_gate_case_passes', 'all_case_check_passes', 'scope_exclusions', 'case_failures')},
        'quality_metrics': metrics,
        'quality_disagreements': paired['disagreements'],
        'judge_roles': {'primary': 'application-model self-evaluation',
                        'second': 'separately configured judge',
                        'different_model_identifiers_verified': comparison['different_model_ids']},
        'independent_review': {key: review[key] for key in ('status', 'reviewer_type', 'reviewed_cases', 'unsafe_case_ids', 'blocking_issues', 'paired_ratings', 'binary_agreement', 'limits')},
        'safety_checks': {key: safety[key] for key in ('runs', 'hard_gate_case_passes', 'all_case_check_passes', 'case_failures')},
        'safety_consistency': consistency,
        'ticket_verification': {role: {key: read(original_paths[role])[key] for key in ('passed', 'handoffs_checked')}
                                for role in ('functional_ticket_readback', 'safety_ticket_readback')},
        'hosted_trace_verified': bool(read(original_paths['final_hosted_trace_readback'])['passed']),
        'demo_checks': [{'scenario': item['scenario'], 'passed': item['passed'], 'checks': item.get('checks', {})} for item in demo['scenarios']],
        'limitations': ['Synthetic fixtures and local mock handoffs; no real transactions.',
                        'Twelve original action-flow criteria are outside the approved scope, not passed.',
                        'Quality metrics retain all misses and unavailable measurements; scores are not averaged into a pass.',
                        'AI proxy review is not actual human calibration.',
                        'Detailed configured identities are withheld from this presentation; results validate only the privately pinned configuration.',
                        'This summary does not establish final submission approval or a new blind-test result.'],
        'original_artifact_sha256': provenance,
        'case_evidence_file': 'final_case_evidence.json',
        'demo_evidence_file': 'demo_evidence.json',
        'submission_ready': False,
    }
    replacements = []
    for role, manifest in (('application_model', main_manifest), ('primary_judge', primary_manifest), ('second_judge', second_manifest)):
        settings = manifest.get('judge_settings', manifest.get('model_settings', {}))
        for key in ('model', 'base_url'):
            if settings.get(key):
                replacements.append((settings[key], '[' + role + ('_endpoint' if key == 'base_url' else '') + ']'))
    verified = tuple(ident for row in raw_functional + raw_safety for result in
                     [row['result'], *row.get('setup_results', [])] for ident in verified_tickets(result))
    verified += tuple(ident for scenario in demo['scenarios'] for result in
        ([scenario['result']] if 'result' in scenario else [t['result'] for t in scenario['turns']])
        for ident in verified_tickets(result))
    outputs = {'evaluation_summary.json': report, 'final_case_evidence.json': case_evidence,
               'demo_evidence.json': demo_evidence}
    env = load_environment(ROOT / '.env')
    secrets = tuple(value for key, value in env.items() if key.endswith('API_KEY') and value)
    serialized = {name: json.dumps(neutral_projection(value, replacements, verified, secrets=secrets), indent=2, allow_nan=False) + '\n'
                  for name, value in outputs.items()}
    if any(digest(path) != provenance[role] for role, path in original_paths.items()):
        raise ValueError('SOURCE_ARTIFACT_CHANGED_DURING_DERIVATION')
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for name, value in serialized.items():
        (args.output_dir / name).write_text(value)
    target = args.output_dir / 'evaluation_summary.json'
    print(json.dumps({'derived_summary': str(target), 'original_artifacts_preserved': True,
                      'submission_ready': False}))


if __name__ == '__main__':
    main()
