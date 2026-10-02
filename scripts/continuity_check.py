#!/usr/bin/env python3
"""Check shot continuity references and asset IDs without contacting a provider."""
import argparse, json
from pathlib import Path

def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('manifest'); p.add_argument('--json',action='store_true'); a=p.parse_args()
    d=json.loads(Path(a.manifest).read_text(encoding='utf-8')); shots=d.get('shots',[]); ids=[s.get('id') for s in shots]; known=set(ids)
    assets=d.get('assets',{}); chars={x.get('id') for x in assets.get('characters',[])}; scenes={x.get('id') for x in assets.get('scenes',[])}; issues=[]
    for i,s in enumerate(shots):
        sid=s.get('id',f'index-{i}'); parent=s.get('continuity_from')
        if parent and parent not in known: issues.append({'shot':sid,'type':'missing_continuity_source','value':parent})
        if parent and parent==sid: issues.append({'shot':sid,'type':'self_continuity_reference','value':parent})
        if parent and parent in known and ids.index(parent)>=i: issues.append({'shot':sid,'type':'forward_continuity_reference','value':parent})
        if s.get('scene') and scenes and s['scene'] not in scenes: issues.append({'shot':sid,'type':'unknown_scene','value':s['scene']})
        for role in s.get('roles',[]):
            if chars and role not in chars: issues.append({'shot':sid,'type':'unknown_character','value':role})
    result={'status':'PASS' if not issues else 'FAIL','shot_count':len(shots),'issues':issues}
    print(json.dumps(result,ensure_ascii=False,indent=2) if a.json else ('PASS: continuity and asset references' if not issues else 'FAIL: '+str(len(issues))+' continuity issues'))
    return 0 if not issues else 1
if __name__=='__main__': raise SystemExit(main())
