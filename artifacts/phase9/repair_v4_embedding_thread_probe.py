import time,json,asyncio
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from capstone_agent.retrieval.chroma_store import PolicySearch
from capstone_agent.retrieval.embeddings_voyage import VoyageNanoEmbeddings
start=time.perf_counter();search=PolicySearch(VoyageNanoEmbeddings());print('loaded',round(time.perf_counter()-start,3),flush=True)
query='return policy calendar days window condition exclusions restocking exceptions '
rows=[]
def probe(stage):
 before=time.perf_counter();result=search.search(query,doc_types=['return_policy'],category='footwear',k=10)
 row={'stage':stage,'seconds':round(time.perf_counter()-before,3),'hits':len(result['results'])};print(json.dumps(row),flush=True);return row
rows.append(probe('main_thread_warmup'))
for i in range(3):rows.append(asyncio.run(asyncio.to_thread(probe,'new_async_executor_'+str(i))))
with ThreadPoolExecutor(max_workers=1) as pool:
 for i in range(3):rows.append(pool.submit(probe,'persistent_executor_'+str(i)).result())
Path('artifacts/phase9/repair_v4_embedding_thread_probe.json').write_text(json.dumps({'rows':rows,'limits':'Public identical query and fixed category, actual pinned local embeddings/index; no customer requests, no model API or holdout. Repeated calls are timing diagnostics, not acceptance or isolation of all OS load.'},indent=2)+'\n')
