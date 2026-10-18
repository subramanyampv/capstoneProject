"""Prose diagnostics cannot drop customer-facing reasons/steps or confuse metadata."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts'))
from judge_response_relevancy import projection


def test_projection_keeps_all_prose_and_prior_conversation_without_metadata():
    row={'result':{'response':{'answer':'Not confirmed.','why':['Evidence is stale.'],'next_steps':['Contact support.'],'citations':[{'source_id':'doc:shipping'}],'outcome_claimed':'ESCALATED'}},
        'setup_results':[{'response':{'answer':'Earlier answer.'}}]}
    query,output=projection(row,'And now?',['Prior question.'])
    assert 'Prior question.' in query and 'Earlier answer.' in query and 'And now?' in query
    assert output=='Not confirmed.\nEvidence is stale.\nContact support.'
    assert 'source_id' not in output and 'ESCALATED' not in output
