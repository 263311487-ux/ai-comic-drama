#!/usr/bin/env python3
"""Create an encoder-independent assembly plan; does not encode media."""
import argparse,json
from pathlib import Path
p=argparse.ArgumentParser(); p.add_argument('manifest'); p.add_argument('--video-dir',default='work/shots'); p.add_argument('--out',required=True); a=p.parse_args()
m=json.loads(Path(a.manifest).read_text()); clips=[]; missing=[]
for s in m.get('shots',[]):
    path=Path(a.video_dir)/f"{s['id']}.mp4"; status='expected' if path.exists() else 'missing'
    if status=='missing': missing.append(s['id'])
    clips.append({'shot_id':s['id'],'path':str(path),'duration':s.get('duration',0),'status':status})
out={'schema_version':'0.1','status':'blocked' if missing else 'ready','video_dir':a.video_dir,'clips':clips,'missing':missing,'note':'Plan only; use an encoder adapter to render.'}
dest=Path(a.out); dest.parent.mkdir(parents=True,exist_ok=True); dest.write_text(json.dumps(out,ensure_ascii=False,indent=2)); print(dest)
