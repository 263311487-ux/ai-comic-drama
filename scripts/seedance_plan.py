#!/usr/bin/env python3
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from ai_comic_drama.seedance import SeedanceCLI
p=argparse.ArgumentParser();p.add_argument('manifest');p.add_argument('--execute',action='store_true');p.add_argument('--shot');a=p.parse_args();m=json.loads(Path(a.manifest).read_text()); provider=SeedanceCLI(execute=a.execute); print(json.dumps({'capabilities':provider.capabilities(),'estimate':provider.estimate(m),'execute':a.execute},ensure_ascii=False,indent=2));
if a.shot:
 s=next(x for x in m['shots'] if x['id']==a.shot); print(json.dumps({'command':provider.command(s)},ensure_ascii=False))
