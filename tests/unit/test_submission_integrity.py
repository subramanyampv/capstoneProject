"""Backend identity and mock-packet integrity are checked at their boundaries."""
import asyncio
import hashlib
import json
import math
import sqlite3
from types import SimpleNamespace
import pytest
from capstone_agent.retrieval.configured_embeddings import ConfiguredEmbeddings
from capstone_agent.retrieval.chroma_store import ingest,PolicySearch
from capstone_agent.support.registry import Registry,ToolContext,SessionIdentity
from capstone_agent.evaluation.export import minimized_json
from test_support_tools import setup
from test_retrieval import FakeModel,corpus_root


def test_index_identity_comes_from_embedding_backend_and_rejects_a_swap(corpus_root):
    embeddings=ConfiguredEmbeddings(model=FakeModel(),dimension=256)
    embeddings.model_id='local/test-model';embeddings.revision='test-revision'
    manifest=ingest(embeddings,root=corpus_root)
    assert manifest['model_id']=='local/test-model' and manifest['model_revision']=='test-revision'
    PolicySearch(embeddings,root=corpus_root,threshold=-1)
    embeddings.backend='openai_compatible'
    with pytest.raises(ValueError,match='MANIFEST_MISMATCH'):
        PolicySearch(embeddings,root=corpus_root,threshold=-1)


def api_embedding(tmp_path):
    (tmp_path/'.env').write_text('EMBEDDING_BACKEND=openai_compatible\nEMBEDDING_MODEL=test-embedding\n'
        'EMBEDDING_REVISION=test-r1\nEMBEDDING_DIMENSION=2\nEMBEDDING_BASE_URL=http://localhost:1234/v1\n')
    return ConfiguredEmbeddings(root=tmp_path)


@pytest.mark.parametrize('vectors,valid',[
    ([[3.,4.],[0.,2.]],True),([[float('nan'),1.],[0.,2.]],False),
    ([[1.],[0.,2.]],False),([[0.,0.],[0.,2.]],False),
])
def test_api_embeddings_validate_count_dimensions_and_normalize(tmp_path,monkeypatch,vectors,valid):
    embedding=api_embedding(tmp_path);requests=[]
    class Client:
        def __init__(self,**kwargs):self.embeddings=self
        def __enter__(self):return self
        def __exit__(self,*args):pass
        def create(self,**kwargs):
            requests.append(kwargs)
            return SimpleNamespace(data=[SimpleNamespace(index=i,embedding=row) for i,row in reversed(list(enumerate(vectors)))])
    monkeypatch.setattr('openai.OpenAI',Client)
    if not valid:
        with pytest.raises(ValueError,match='EMBEDDING_REQUEST_FAILED'):embedding.embed_documents(['one','two'])
    else:
        result=embedding.embed_documents(['one','two'])
        assert result[0]==[.6,.8] and math.isclose(sum(x*x for x in result[1]),1.)
        assert requests==[{'model':'test-embedding','input':['one','two'],'dimensions':2}]


def test_api_backend_requires_explicit_identity(tmp_path):
    (tmp_path/'.env').write_text('EMBEDDING_BACKEND=openai_compatible\n')
    with pytest.raises(ValueError,match='EXPLICIT_EMBEDDING_CONFIGURATION_REQUIRED'):ConfiguredEmbeddings(root=tmp_path)


def test_finite_large_vectors_normalize_without_overflow():
    embeddings=ConfiguredEmbeddings(model=FakeModel(),dimension=256)
    vector=embeddings._vectors([[1e300]*256])[0]
    assert math.isclose(sum(x*x for x in vector),1.)
    with pytest.raises(ValueError,match='INVALID_EMBEDDING_DIMENSION'):
        ConfiguredEmbeddings(model=FakeModel(),dimension=0)


def test_ticket_digest_covers_stored_packet_and_detects_corruption(setup):
    services,_=setup;ctx=ToolContext(SessionIdentity('C-100'));ctx.triggers.add('T1')
    registry=Registry(services,ctx)
    args={'triggers':['T1'],'summary':'Product safety review.','evidence_refs':[]}
    first=asyncio.run(registry.call('escalation','create_escalation',args))
    assert first.status=='ok'
    with sqlite3.connect(services.ticket_path) as db:
        key,payload=db.execute('SELECT key,payload FROM tickets').fetchone()
        stored=json.loads(payload)
        digest=hashlib.sha256(json.dumps(stored['packet'],sort_keys=True,separators=(',',':')).encode()).hexdigest()
        assert first.data['packet_hash']==digest
        stored['packet']['priority']='normal'
        db.execute('UPDATE tickets SET payload=? WHERE key=?',(json.dumps(stored),key))
    second=asyncio.run(registry.call('escalation','create_escalation',args))
    assert second.status=='error' and second.error=='TICKET_INTEGRITY_FAILED'


def test_export_preserves_digest_bytes_but_still_redacts_configured_credentials():
    digest='1234567890abcdef'*4
    record={'summary_hash':digest,'packet_hash':digest,'answer':'phone 123-456-7890'}
    exported=json.loads(minimized_json(record))
    assert exported['summary_hash']==exported['packet_hash']==digest
    assert '123-456-7890' not in exported['answer']
    assert digest not in minimized_json(record,(digest,))
