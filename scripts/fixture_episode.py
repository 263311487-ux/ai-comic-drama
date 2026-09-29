#!/usr/bin/env python3
"""Generate tiny local MP4 shot fixtures for encoder/QA tests."""
import argparse, json, shutil, subprocess
from pathlib import Path
p=argparse.ArgumentParser(); p.add_argument('--manifest',required=True); p.add_argument('--out',required=True); a=p.parse_args()
if not shutil.which('ffmpeg'): raise SystemExit('ffmpeg not found')
m=json.loads(Path(a.manifest).read_text()); root=Path(a.out); shots=root/'制作成果'/'video'; shots.mkdir(parents=True,exist_ok=True)
for s in m.get('shots',[]):
    subprocess.run(['ffmpeg','-y','-loglevel','error','-f','lavfi','-i','color=c=navy:s=270x480:d='+str(s.get('duration',1)),'-f','lavfi','-i','sine=frequency=440:sample_rate=48000:duration='+str(s.get('duration',1)),'-filter:a','loudnorm=I=-18:TP=-2:LRA=7','-shortest','-c:v','libx264','-c:a','aac',str(shots/f"{s['id']}.mp4")],check=True)
print(root)
