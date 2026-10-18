"""Review packets include operation receipts rather than asking reviewers to infer success."""
import hashlib
import json
import sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts'))
from judge_final_suite import human_packet


def test_evidence_v2_includes_failed_tools_and_feedback_and_locks_exact_packet(tmp_path):
    (tmp_path/'manifest.json').write_text(json.dumps({'context_file':'frozen_contexts_v3.json','review_packet_format':'evidence-v2','build_sha256':{'fixture':'hash'}}))
    (tmp_path/'outputs.jsonl').write_bytes(b'locked output bytes')
    row={'case_id':'N01','setup_results':[],'feedback':[{'signal':'too_long','type':'implicit'}],
         'result':{'results':[],'outcome':'INSUFFICIENT_EVIDENCE','response':{'answer':'I could not confirm.','why':[],'citations':[]},
             'ticket':None,'refusals':[],'triggers':[], 'tool_records':[{'name':'get_tracking_events','status':'error','error':'TIMEOUT'}]}}
    human_packet(tmp_path,[row],{'N01':{'input':'A synthetic question.'}})
    packet=(tmp_path/'human_review.md').read_bytes();text=packet.decode()
    assert 'feedback_receipts' in text and 'too_long' in text and 'TIMEOUT' in text
    lock=json.loads((tmp_path/'review_packet_manifest.json').read_text())
    assert lock['review_packet_sha256']==hashlib.sha256(packet).hexdigest()
    assert lock['source_outputs_sha256']==hashlib.sha256(b'locked output bytes').hexdigest()
    row['result']['response']['answer']='Changed answer.'
    with pytest.raises(ValueError,match='EXISTING_REVIEW_PACKET'):human_packet(tmp_path,[row],{'N01':{'input':'A synthetic question.'}})
    assert (tmp_path/'human_review.md').read_bytes()==packet
