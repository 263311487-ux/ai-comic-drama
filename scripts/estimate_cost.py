#!/usr/bin/env python3
"""Estimate video charges in currency units per generated second."""
import argparse,json,math
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument('manifest')
p.add_argument('--rate',type=float,required=True,help='currency units per generated second')
p.add_argument('--pass-rate',type=float,default=1)
p.add_argument('--versions',type=int,default=1)
a=p.parse_args()
if not math.isfinite(a.rate) or a.rate<0 or not math.isfinite(a.pass_rate) or not 0<a.pass_rate<=1 or a.versions<1:
 p.error('rate must be finite and nonnegative; pass-rate in (0,1]; versions >= 1')
d=json.loads(Path(a.manifest).read_text())
seconds=sum(s['duration'] for s in d['shots'])
if not math.isfinite(seconds) or seconds<=0: p.error('positive finite episode duration required')
factor=a.versions/a.pass_rate
print(json.dumps({'source_seconds':seconds,'estimated_generated_seconds':seconds*factor,'estimated_attempts':len(d['shots'])*factor,'estimated_cost':seconds*factor*a.rate,'rate_unit':'currency per generated second','excludes':['images','audio','tax','provider-specific fees']},indent=2))
