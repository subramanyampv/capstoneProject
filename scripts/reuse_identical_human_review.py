"""Carry real ratings only when the entire displayed case packet is identical."""
import argparse
import hashlib
import json
import re
from pathlib import Path

FIELDS=('faithfulness','answer_relevancy','grounded_support','not_applicable_metrics','unsafe_or_fabricated_claim','comment')

def blocks(text):
    parts=re.split(r'^## ([A-Z][0-9]{2})\s*$',text,flags=re.M)
    return {parts[i]:parts[i+1].strip() for i in range(1,len(parts),2)}

def reuse(old_packet,new_packet,old_review,new_review):
    if old_review.get('status')!='reviewed_by_human':raise ValueError('ACTUAL_SOURCE_HUMAN_REVIEW_REQUIRED')
    if new_review.get('status')!='awaiting_human_review':raise ValueError('DO_NOT_OVERWRITE_STARTED_OR_COMPLETED_REVIEW')
    before=blocks(old_packet);after=blocks(new_packet);source={r['case_id']:r for r in old_review['cases']}
    copied=[];pending=[]
    for row in new_review['cases']:
        ident=row['case_id']
        if any(row.get(k) is not None for k in ['faithfulness','answer_relevancy','grounded_support','unsafe_or_fabricated_claim']) or row.get('comment'):
            raise ValueError('DO_NOT_OVERWRITE_EXISTING_RATINGS')
        if ident in source and before.get(ident) is not None and before[ident]==after.get(ident):
            for key in FIELDS:row[key]=source[ident].get(key)
            row['rating_provenance']={'kind':'actual_prior_human_rating_identical_complete_case_packet',
                'case_packet_sha256':hashlib.sha256(after[ident].encode()).hexdigest()}
            copied.append(ident)
        else:pending.append(ident)
    # Never claim a new human review or silently complete a partially reviewed packet.
    return {'reused_identical_case_ids':copied,'needs_actual_review_case_ids':pending,
        'limits':'Only exact complete displayed case blocks qualify: question, prior turns, answer, reasons, citations, obligations/audit and evidence. Changed answers/evidence retain empty ratings. Original ratings remain actual human input; status remains awaiting_human_review until user confirmation.'}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('source_run',type=Path);parser.add_argument('target_run',type=Path);args=parser.parse_args()
    old=json.loads((args.source_run/'human_review_template.json').read_text());new=json.loads((args.target_run/'human_review_template.json').read_text())
    report=reuse((args.source_run/'human_review.md').read_text(),(args.target_run/'human_review.md').read_text(),old,new)
    report['source_run']=args.source_run.name;report['target_run']=args.target_run.name
    (args.target_run/'human_review_template.json').write_text(json.dumps(new,indent=2)+'\n')
    (args.target_run/'human_review_reuse.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

if __name__=='__main__':main()
