#!/usr/bin/env python3
import argparse,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('manifest');p.add_argument('--rate',type=float,required=True);p.add_argument('--pass-rate',type=float,default=1);p.add_argument('--versions',type=int,default=1);a=p.parse_args();d=json.loads(Path(a.manifest).read_text());n=len(d.get('shots',[]));sec=sum(s.get('duration',0) for s in d.get('shots',[]));attempts=n*a.versions/max(a.pass_rate,.01);print(f'seconds={sec:.2f}\nshots={n}\nestimated_attempts={attempts:.2f}\nestimated_cost={attempts*a.rate:.2f}')
