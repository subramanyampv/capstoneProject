"""Local, opt-in style learning. No text, vectors, tool permissions or policies persist here."""
import json
import math
import os
import re
import threading
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from pathlib import Path
import fcntl
from capstone_agent.support.privacy import opaque

SIGNALS=frozenset({'too_long','too_short','unclear','helpful','not_helpful'})
COMMANDS=SIGNALS|{'enable','disable','reset_style'}
VERBOSITY=('concise','standard','detailed')
FORMATS=('prose','bullets','step_by_step')
REPEAT_THRESHOLD=.98  # conservative development default; not a calibrated semantic metric
_LOCK=threading.RLock()

@dataclass(frozen=True)
class StyleProfile:
    verbosity:str='standard'
    format:str='prose'
    version:int=0

    def __post_init__(self):
        if self.verbosity not in VERBOSITY or self.format not in FORMATS or type(self.version) is not int or self.version<0:
            raise ValueError('INVALID_STYLE_PROFILE')

    def as_dict(self):return {'verbosity':self.verbosity,'format':self.format,'version':self.version}

    def instruction(self):
        length={'concise':'Aim for at most 80 words in answer.', 'standard':'Aim for at most 140 words in answer.',
                'detailed':'Aim for at most 250 words in answer, with useful explanations.'}[self.verbosity]
        form='step_by_step' if self.format=='step_by_step' else ('bullets' if self.verbosity=='concise' else self.format)
        return length+' '+{'prose':'Use ordinary prose.','bullets':'Use Markdown bullet points.',
            'step_by_step':'Use numbered steps.'}[form]+' Safety disclosures, evidence, citations and intent coverage take priority over style. Never change eligibility, escalation or tool permissions.'


def is_preference_command(query):
    return isinstance(query,str) and (query.strip()=='/forget-preferences' or query.strip().split(maxsplit=1)[0:1]==['/feedback'])

class PreferenceStore:
    """Single-machine lock and atomic file replacement; history 20, signals 10, feedback 30 days.

    prefs.json is authoritative. feedback.jsonl is a recoverable derived report, rebuilt on access.
    A crash between replacements cannot resurrect a deleted authoritative preference.
    """
    def __init__(self,root):self.directory=Path(root)/'data/runtime'

    @contextmanager
    def transaction(self):
        self.directory.mkdir(parents=True,exist_ok=True)
        with _LOCK, (self.directory/'preferences.lock').open('a') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX)
            try:
                path=self.directory/'prefs.json'
                data=json.loads(path.read_text()) if path.exists() else {'profiles':{},'feedback':[]}
                cutoff=(datetime.now(timezone.utc)-timedelta(days=30)).isoformat()
                data['feedback']=[r for r in data['feedback'] if r['ts']>=cutoff]
                yield data
                self._write(path,json.dumps(data,indent=2)+'\n')
                self._write(self.directory/'feedback.jsonl',''.join(json.dumps(r)+'\n' for r in data['feedback']))
            finally:fcntl.flock(lock,fcntl.LOCK_UN)

    def _write(self,path,text):
        temp=path.with_name(path.name+'.'+uuid.uuid4().hex+'.tmp')
        try:
            with temp.open('x') as stream:
                os.chmod(temp,0o600);stream.write(text);stream.flush();os.fsync(stream.fileno())
            os.replace(temp,path)
        finally:temp.unlink(missing_ok=True)

    def profile(self,customer):
        with self.transaction() as data:
            row=data['profiles'].get(opaque(customer),{})
            return StyleProfile(**row.get('style',{})) if row.get('consent') else StyleProfile()

    def consented(self,customer):
        with self.transaction() as data:return data['profiles'].get(opaque(customer),{}).get('consent',False)

    def apply(self,customer,signal,*,kind='explicit',request_id=None):
        if signal not in COMMANDS or kind not in {'explicit','implicit'}:raise ValueError('INVALID_FEEDBACK')
        # Never accept caller-selected identifiers containing free text.
        request_id=request_id or uuid.uuid4().hex
        if not re.fullmatch(r'[0-9a-f]{32}',request_id):raise ValueError('INVALID_FEEDBACK_REFERENCE')
        key=opaque(customer);now=datetime.now(timezone.utc).isoformat()
        with self.transaction() as data:
            row=data['profiles'].get(key)
            if kind=='implicit' and (not row or not row['consent']):return StyleProfile()
            if not row:
                row={'consent':True,'consent_at':now,'style':StyleProfile().as_dict(),'signals':[],'history':[]}
                data['profiles'][key]=row
            old=StyleProfile(**row['style']);new=old
            if signal=='disable':row['consent']=False;row['consent_at']=now;row['signals']=[]
            elif signal=='enable':row['consent']=True;row['consent_at']=now
            elif signal=='reset_style':
                new=StyleProfile(version=old.version+1);row['signals']=[]
            else:
                if kind=='explicit':row['consent']=True;row['consent_at']=now
                # Deduplicate only within retained feedback; IDs come from application requests.
                if any(r['customer_ref']==key and r['request_id']==request_id and r['signal']==signal for r in data['feedback']):return old
                event={'ts':now,'customer_ref':key,'request_id':request_id,'signal':signal,'type':kind}
                data['feedback'].append(event)
                # Bound report storage as well as each customer's adaptation window.
                data['feedback']=data['feedback'][-10000:]
                row['signals']=(row['signals']+[{'signal':signal,'used':False}])[-10:]
                matching=[r for r in row['signals'] if r['signal']==signal and not r['used']]
                if len(matching)>=2 and signal in {'too_long','too_short','unclear'}:
                    verbosity=old.verbosity;form=old.format
                    if signal=='unclear':form='step_by_step'
                    else:verbosity=VERBOSITY[max(0,min(2,VERBOSITY.index(verbosity)+(-1 if signal=='too_long' else 1)))]
                    for r in matching:r['used']=True
                    if (verbosity,form)!=(old.verbosity,old.format):new=StyleProfile(verbosity,form,old.version+1)
            if new!=old:
                row['history']=(row['history']+[{'from':old.as_dict(),'to':new.as_dict(),'reason':signal,
                    'signals':[signal]* (2 if signal in SIGNALS else 0),'ts':now}])[-20:]
                row['style']=new.as_dict()
            return new if row['consent'] else StyleProfile()

    def forget(self,customer):
        with self.transaction() as data:
            key=opaque(customer);data['profiles'].pop(key,None)
            data['feedback']=[r for r in data['feedback'] if r['customer_ref']!=key]


def implicit_signal(query,context,*,embeddings=None):
    """Only successful prior answers qualify; compare transient masked text, never persist vectors."""
    if context.get('last_outcome')!='ANSWERED':return None
    if re.search(r'\b(?:shorter|too long|tl;?dr|summarize)\b',query,re.I):return 'too_long'
    if re.search(r'\b(?:more detail|explain more)\b|^\s*why\??\s*$',query,re.I):return 'too_short'
    previous=[m['content'] for m in context.get('messages',[]) if m['role']=='user'][-2:]
    if not embeddings or not previous:return None
    # Changed record/product references must not become negative feedback.
    refs=lambda text:set(m.upper() for m in re.findall(r'\b(?:O-\d{4}|SKU-[A-Z0-9-]+)\b',text,re.I))
    for old in previous:
        if refs(query)!=refs(old):continue
        try:
            a=embeddings.embed_query(query);b=embeddings.embed_query(old)
            if len(a)!=len(b) or not a:continue
            norm=math.sqrt(sum(x*x for x in a)*sum(x*x for x in b))
            similarity=sum(x*y for x,y in zip(a,b))/norm if norm else 0
            if math.isfinite(similarity) and similarity>=REPEAT_THRESHOLD:return 'unclear'
        except Exception:
            # Optional adaptation failures cannot suppress support or escalation.
            return None
    return None
