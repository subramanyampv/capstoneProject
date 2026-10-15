"""Bounded in-process LangGraph projection; never checkpoint the working support graph."""
import hashlib
import re
import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass,field
from typing import TypedDict
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph,START,END
from langsmith import tracing_context
from capstone_agent.support.privacy import mask_sensitive

ALLOWED_INTENTS=frozenset({'order_tracking','shipping_tracking','order_lookup','return_eligibility','refund_request','refund_eligibility','cancellation','warranty','product_information','policy_question','support_request','feedback_style','escalation_request'})
ORDER=re.compile(r'\bO-\d{4}\b',re.I)
ORDER_REFERENCE=re.compile(r'\border\b|\b(?:track|cancel)\s+it\b',re.I)
OTHER=re.compile(r'\b(?:other|previous)\s+order\b',re.I)
REFERENCE=re.compile(r'\b(?:that|this|same|my|other|previous)\s+order\b|\b(?:track|cancel|return)\s+(?:it|them)\b|\b(?:its|their)\s+(?:material|size|care|warranty|status)\b|\b(?:the shoes|the jacket|the speaker|the pots)\b',re.I)

class Projection(TypedDict):
    messages:list[dict]
    entities:dict
    last_intents:list[str]
    last_outcome:str|None

@dataclass
class Entry:
    lock:threading.RLock=field(default_factory=threading.RLock)
    users:int=0
    last_seen:float|None=None

class SessionMemory:
    def __init__(self,*,ttl_seconds=1800,max_sessions=100,clock=time.monotonic,background=False):
        if ttl_seconds<=0 or max_sessions<1: raise ValueError('INVALID_MEMORY_CONFIGURATION')
        self.ttl_seconds,self.max_sessions,self.clock=ttl_seconds,max_sessions,clock
        self.saver=InMemorySaver(); self._entries={}; self._lock=threading.RLock()
        graph=StateGraph(Projection)
        graph.add_node('retain_projection',lambda state:{})
        graph.add_edge(START,'retain_projection');graph.add_edge('retain_projection',END)
        self.graph=graph.compile(checkpointer=self.saver)
        self._stop=threading.Event()
        self._reaper=None
        if background:
            import weakref
            ref=weakref.ref(self);stop=self._stop;interval=min(30.,ttl_seconds/2)
            def reap():
                while not stop.wait(interval):
                    memory=ref()
                    if memory is None:return
                    with memory._lock:memory._sweep()
                    del memory
            self._reaper=threading.Thread(target=reap,name='support-memory-expiry',daemon=True)
            self._reaper.start()

    def close(self):
        self._stop.set()
        with self._lock:
            for key,entry in list(self._entries.items()):
                if entry.users:raise ValueError('MEMORY_SESSION_BUSY')
                self._drop(key,entry)
            self._entries.clear()

    def key(self,identity):
        return 'memory:'+hashlib.sha256((identity.customer_id+'\0'+identity.session_id).encode()).hexdigest()

    def config(self,key): return {'configurable':{'thread_id':key},'callbacks':[]}

    def _drop(self,key,entry):
        self.saver.delete_thread(key);entry.last_seen=None

    def _sweep(self,exclude=None):
        now=self.clock()
        for key,entry in list(self._entries.items()):
            if key!=exclude and not entry.users and entry.last_seen is not None and now-entry.last_seen>=self.ttl_seconds:
                self._drop(key,entry);del self._entries[key]

    @contextmanager
    def session(self,identity):
        key=self.key(identity)
        with self._lock:
            self._sweep(key)
            if key not in self._entries:
                if len(self._entries)>=self.max_sessions:
                    idle=[(e.last_seen or 0,k,e) for k,e in self._entries.items() if not e.users]
                    if not idle: raise ValueError('MEMORY_CAPACITY_EXCEEDED')
                    _,old,entry=min(idle);self._drop(old,entry);del self._entries[old]
                self._entries[key]=Entry()
            entry=self._entries[key];entry.users+=1
        try:
            with entry.lock:
                expired=entry.last_seen is not None and self.clock()-entry.last_seen>=self.ttl_seconds
                if expired:self._drop(key,entry)
                yield key,entry,expired
        finally:
            with self._lock:entry.users-=1

    def _read(self,key):
        with tracing_context(enabled=False):
            saved=self.saver.get_tuple(self.config(key))
        values=saved.checkpoint['channel_values'] if saved else {}
        return {name:values.get(name,default) for name,default in
                [('messages',[]),('entities',{}),('last_intents',[]),('last_outcome',None)]}

    def snapshot(self,identity):
        with self.session(identity) as (key,_,__):return self._read(key)

    def reset(self,identity):
        with self.session(identity) as (key,entry,_):self._drop(key,entry)

    def _save(self,key,entry,projection):
        # Delete all earlier checkpoints/writes/blobs BEFORE passing only a safe
        # projection to a separate graph. Intermediate snapshots are safe too.
        self.saver.delete_thread(key)
        with tracing_context(enabled=False):self.graph.invoke(projection,self.config(key),durability="sync")
        entry.last_seen=self.clock()

    def process(self,query,identity,execute,*,enabled=True,secrets=()):
        if not isinstance(query,str) or not query.strip() or len(query)>2000:raise ValueError('INVALID_SUPPORT_INPUT')
        with self.session(identity) as (key,entry,expired):
            old=self._read(key) if enabled else {'messages':[],'entities':{},'last_intents':[],'last_outcome':None}
            if not enabled:self._drop(key,entry)
            if query.strip()=='/reset':
                self._drop(key,entry)
                return command_result(enabled)
            explicit=list(dict.fromkeys(m.upper() for m in ORDER.findall(query)))
            entities=dict(old['entities']);other=bool(OTHER.search(query))
            references=bool(REFERENCE.search(query))
            resolved=None
            if len(explicit)==1:resolved=explicit[0]
            elif not explicit and references:
                resolved=entities.get('previous_order_id') if other else entities.get('order_id')
            needs=bool(len(explicit)>1 or (references and not resolved and (ORDER_REFERENCE.search(query) or not entities.get('sku'))))
            streak=0
            for message in reversed(old['messages']):
                if message['role']!='assistant':continue
                if message['content']!='CLARIFICATION_REQUESTED':break
                streak+=1
            context={'enabled':enabled,'messages':old['messages'][-6:],'entities':entities,
                     'last_intents':old['last_intents'],'last_outcome':old['last_outcome'],
                     'resolved_order_id':resolved,'resolved_sku':entities.get('sku') if references and not explicit and not other else None,
                     'needs_clarification':needs,'previous_clarifications':streak,'expired':expired}
            result=execute(query,context)
            if enabled:
                next_entities=dict(entities);next_entities.pop('previous_order_id',None)
                # A new explicit identifier clears old context even when it fails ownership.
                if explicit:next_entities={}
                verified_order=None;verified_product=None
                for record in result.get('tool_records',[]):
                    if record['status']!='ok':continue
                    if record['name']=='lookup_order' and record['data']['order_id']==resolved:
                        verified_order=record['data']
                    if record['name']=='get_product_details':verified_product=record['data']
                facts=[fact for item in result.get('results',[]) for fact in item['facts'].get('tools',[])]
                if not verified_order and resolved:
                    for fact in facts:
                        if fact['name'] in {'get_tracking_events','check_return_eligibility'} and fact['args']['order_id']==resolved:
                            items=([{'sku':fact['args']['sku']}] if fact['name']=='check_return_eligibility' else [])
                            verified_order={'order_id':resolved,'items':items}
                if verified_order:
                    order=verified_order['order_id']
                    next_entities={'order_id':order}
                    if len(verified_order['items'])==1:
                        item=verified_order['items'][0];next_entities['sku']=item['sku']
                        if item.get('name'):next_entities['product_name']=item['name']
                    if explicit and entities.get('order_id') and entities['order_id']!=order:
                        next_entities['previous_order_id']=entities['order_id']
                elif explicit or (resolved and any(r['status']=='error' and r['error']=='NOT_FOUND' and
                    r['name'] in {'lookup_order','get_tracking_events','check_return_eligibility'} for r in result.get('tool_records',[]))):
                    next_entities={}
                if verified_product:
                    if next_entities.get('order_id') and next_entities.get('sku')!=verified_product['sku']:next_entities={}
                    next_entities.update(sku=verified_product['sku'],product_name=verified_product['name'])
                intents=list(dict.fromkeys(v if v in ALLOWED_INTENTS else 'support_request' for v in result['response'].get('intents_addressed',[])))[:8]
                # Assistant prose contains record/policy facts: retain only its outcome marker.
                messages=(old['messages']+[{'role':'user','content':mask_sensitive(query,secrets)},
                          {'role':'assistant','content':result['outcome']}])[-6:]
                self._save(key,entry,{'messages':messages,'entities':next_entities,
                    'last_intents':intents,'last_outcome':result['outcome']})
            result['memory']={'enabled':enabled,'history_messages':len(old['messages']),
                'resolved_reference':bool(references and resolved and not explicit),'expired':expired,'reset':False}
            return result

def command_result(enabled):
    return {'response':{'answer':'Session memory cleared. Which order or product would you like help with?',
        'why':[],'citations':[],'next_steps':[],'intents_addressed':['reset'],'outcome_claimed':'COMMAND_HANDLED'},
        'outcome':'COMMAND_HANDLED','ticket':None,'refusals':[],'triggers':[],'tool_records':[],
        'results':[],'stages':['command_handler','memory_reset'],'errors':[],'model_calls':0,'tool_calls':0,
        'handoffs':0,'replans':0,'repairs':0,'tokens':0,'safety_version':None,'latency_ms':0.,
        'memory':{'enabled':enabled,'history_messages':0,'resolved_reference':False,'expired':False,'reset':True}}
