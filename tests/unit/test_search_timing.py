"""Local profiling records neither search text nor exception content."""
import json
import sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts'))
from run_final_suite import SerializedSearch


def test_timing_records_safe_boundaries_on_success_and_error():
    class Fake:
        def search(self,text):
            if text=='canary.jane@example.test':raise ValueError(text)
            return {'results':[]}
    search=SerializedSearch(Fake())
    assert search.search('private customer question')=={'results':[]}
    with pytest.raises(ValueError):search.search('canary.jane@example.test')
    assert [r['status'] for r in search.timings]==['ok','error']
    assert all(r['queue_ms']>=0 and r['search_execution_ms']>=0 for r in search.timings)
    encoded=json.dumps(search.timings)
    assert 'private customer question' not in encoded and 'canary.jane@example.test' not in encoded
