"""Streamlit exposes the real support adapter without invoking a provider in tests."""
from pathlib import Path
from unittest.mock import patch, MagicMock
from streamlit.testing.v1 import AppTest

ROOT=Path(__file__).resolve().parents[2]

def test_support_mode_binds_selected_synthetic_identity_and_renders_sources():
    fake={'response':{'answer':'I could not confirm the handoff. Contact retailer support.',
        'why':['The mock ticket store did not confirm creation.'],
        'citations':[{'source_id':'doc:return_policy','section':'window','record_version':'v1'}],
        'next_steps':['Contact retailer support directly.']},'outcome':'ESCALATION_FAILED_DISCLOSED'}
    with patch('capstone_agent.retrieval.embeddings_voyage.VoyageNanoEmbeddings',return_value=object()), \
         patch('capstone_agent.retrieval.chroma_store.PolicySearch',return_value=MagicMock()), \
         patch('capstone_agent.support.runtime.run_support',return_value=fake) as runner:
        ui=AppTest.from_file(str(ROOT/'streamlit_app.py')).run(timeout=30)
        ui.radio[0].set_value('Support agent').run()
        account=next(s for s in ui.selectbox if s.label=='Synthetic account')
        account.set_value('C-103').run()
        ui.text_area[0].set_value('Please review my refund.')
        next(b for b in ui.button if b.label=='Get answer').click().run()
        assert not ui.exception
        assert runner.call_args.kwargs['identity'].customer_id=='C-103'
        assert any('could not confirm' in m.value for m in ui.markdown)
        assert any('doc:return_policy' in m.value for m in ui.markdown)

def test_new_session_control_deletes_the_previous_memory_scope():
    from capstone_agent.support.runtime import MEMORY
    with patch.object(MEMORY,'reset',wraps=MEMORY.reset) as reset:
        ui=AppTest.from_file(str(ROOT/'streamlit_app.py')).run(timeout=30)
        ui.radio[0].set_value('Support agent').run()
        old=ui.session_state['support_identity']
        next(b for b in ui.button if b.label=='New support session').click().run()
        assert not ui.exception and ui.session_state['support_identity'].session_id!=old.session_id
        reset.assert_called_with(old)

def test_feedback_buttons_share_runtime_and_follow_selected_account():
    fake={'response':{'answer':'Verified product information.','why':[],'citations':[], 'next_steps':[]},
          'outcome':'ANSWERED','style':{'version':0,'verbosity':'standard','format':'prose'}}
    with patch('capstone_agent.retrieval.embeddings_voyage.VoyageNanoEmbeddings',return_value=object()), \
         patch('capstone_agent.retrieval.chroma_store.PolicySearch',return_value=MagicMock()), \
         patch('capstone_agent.support.runtime.run_support',return_value=fake) as runner:
        ui=AppTest.from_file(str(ROOT/'streamlit_app.py')).run(timeout=30)
        ui.radio[0].set_value('Support agent').run()
        ui.text_area[0].set_value('What is the material?')
        next(b for b in ui.button if b.label=='Get answer').click().run()
        next(b for b in ui.button if b.label=='Too long').click().run()
        assert runner.call_args.args==('/feedback too_long',)
        assert runner.call_args.kwargs['identity'].customer_id=='C-100'
        assert any('Verified product' in m.value for m in ui.markdown) # retained through rerun
        next(s for s in ui.selectbox if s.label=='Synthetic account').set_value('C-101').run()
        assert not any(b.label=='Too long' for b in ui.button)
        next(b for b in ui.button if b.label=='Delete preferences').click().run()
        assert runner.call_args.args==('/forget-preferences',)
        assert runner.call_args.kwargs['identity'].customer_id=='C-101'
        assert not ui.exception
