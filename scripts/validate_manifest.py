#!/usr/bin/env python3
import json,sys
from pathlib import Path
def main(p):
 try:d=json.loads(Path(p).read_text())
 except Exception as e: print('ERROR: invalid JSON:',e); return 1
 ok=True
 for k in ['schema_version','episode_id','title','ratio','delivery','provider','budget','shots']:
  if k not in d: print('ERROR: missing',k); ok=False
 if d.get('ratio') not in {'9:16','16:9','1:1','21:9'}: print('ERROR: invalid ratio'); ok=False
 for k in ('width','height','fps'):
  if not isinstance(d.get('delivery',{}).get(k),(int,float)) or d['delivery'][k]<=0: print('ERROR: invalid delivery.'+k); ok=False
 ids=[]; refs={a.get('id') for a in d.get('assets',{}).get('characters',[])}|{a.get('id') for a in d.get('assets',{}).get('scenes',[])}
 for i,s in enumerate(d.get('shots',[])):
  sid=s.get('id',f'index-{i}')
  if sid in ids: print('ERROR: duplicate shot',sid); ok=False
  ids.append(sid)
  for k in ('id','duration','purpose','action','camera','end_state'):
   if not s.get(k): print(f'ERROR: {sid} missing {k}'); ok=False
  if not isinstance(s.get('duration'),(int,float)) or s.get('duration',0)<=0: print('ERROR: invalid duration',sid); ok=False
  if refs and s.get('scene') and s['scene'] not in refs: print('ERROR: unknown scene',s['scene']); ok=False
  for role in s.get('roles',[]):
   if refs and role not in refs: print('ERROR: unknown role',role); ok=False
 if ok: print(f"PASS: {d.get('episode_id')} ({len(d.get('shots',[]))} shots)")
 return 0 if ok else 1
if __name__=='__main__': sys.exit(main(sys.argv[1]) if len(sys.argv)>1 else 2)
