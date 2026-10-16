import json
from pathlib import Path
from capstone_agent.retrieval.embeddings_voyage import VoyageNanoEmbeddings,MODEL_ID,REVISION
from capstone_agent.support.preferences import implicit_signal,REPEAT_THRESHOLD
root=Path(__file__).resolve().parents[1]
emb=VoyageNanoEmbeddings()
context={'last_outcome':'ANSWERED','messages':[{'role':'user','content':'What is the material of TrailRunner Shoes?'}]}
cases=[('exact_repeat','What is the material of TrailRunner Shoes?','unclear'),
       ('paraphrase','What are TrailRunner Shoes made of?',None),
       ('different_product','What is the material of Alpine Jacket?',None)]
rows=[]
for label,query,expected in cases:
 signal=implicit_signal(query,context,embeddings=emb)
 rows.append({'case':label,'signal':signal,'expected_for_probe':expected,'matched':signal==expected})
report={'model':MODEL_ID,'revision':REVISION,'threshold':REPEAT_THRESHOLD,'results':rows,
    'limits':'Three authored development probes; paraphrase expectation records conservative behavior, not a calibrated positive label. No vector persisted or holdout used.'}
(root/'artifacts/phase7_repeat_probe.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
