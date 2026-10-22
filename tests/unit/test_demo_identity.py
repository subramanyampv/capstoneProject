"""Demo evidence must use the frozen run's effective configuration."""
import hashlib
import importlib
import json
from pathlib import Path

import pytest

from capstone_agent.config import LLMConfig


@pytest.mark.parametrize('change', ['none', 'timeout', 'identity', 'build'])
def test_demo_rejects_candidate_drift_before_live_work(monkeypatch, change):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[2] / 'scripts'))
    demo = importlib.import_module('replay_submission_demo')
    baseline = LLMConfig(base_url='http://localhost:1234/v1', model='synthetic-application', timeout_seconds=60)
    manifest = {'build_sha256': {'synthetic.py': 'baseline'},
                'model_config_sha256': hashlib.sha256(json.dumps(
                    {'settings': baseline.public_settings(), 'endpoint': baseline.base_url},
                    sort_keys=True).encode()).hexdigest()}
    current = LLMConfig(base_url=baseline.base_url,
                        model='other-synthetic-application' if change == 'identity' else baseline.model,
                        timeout_seconds=20 if change == 'timeout' else 60)
    monkeypatch.setattr(demo, 'build_hashes', lambda: {'synthetic.py': 'changed' if change == 'build' else 'baseline'})
    monkeypatch.setattr(demo.LLMConfig, 'from_env', lambda _: current)
    if change == 'none':
        demo.assert_candidate(manifest)
    else:
        with pytest.raises(ValueError, match='DEMO_(BUILD|CONFIGURATION)_DIFFERS_FROM_FROZEN_RUN'):
            demo.assert_candidate(manifest)
