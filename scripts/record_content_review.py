#!/usr/bin/env python3
"""Record a human content-review result in the publish-gate QA schema."""
import argparse,json,time
from pathlib import Path
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',required=True); p.add_argument('--status',choices=['PASS','FAIL','PENDING_HUMAN_REVIEW'],required=True)
    p.add_argument('--reviewer',required=True); p.add_argument('--basis',required=True); p.add_argument('--shot',action='append',default=[])
    a=p.parse_args()
    if not a.reviewer.strip() or not a.basis.strip(): p.error('--reviewer and --basis must be nonempty')
    o={'schema_version':'0.1','status':a.status,'review_type':'content','reviewer':a.reviewer,'basis':a.basis,'created_at':int(time.time()),'publish_approval':False,'shots':[{'id':x,'status':'REVIEWED' if a.status=='PASS' else a.status} for x in a.shot]}
    out=Path(a.out); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print(out)

if __name__ == '__main__': main()
