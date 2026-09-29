#!/usr/bin/env python3
import argparse,json,datetime
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--manifest',required=True);p.add_argument('--out',required=True);a=p.parse_args();d=json.loads(Path(a.manifest).read_text());o={'schema_version':'0.1','created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'PENDING_HUMAN_REVIEW','shots':[{'id':s['id'],'status':'UNREVIEWED','l1':False,'l2':False,'l3':False} for s in d.get('shots',[])]};Path(a.out).parent.mkdir(parents=True,exist_ok=True);Path(a.out).write_text(json.dumps(o,ensure_ascii=False,indent=2));print('WROTE',a.out)
