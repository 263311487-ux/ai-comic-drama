#!/usr/bin/env python3
"""Optional ffmpeg encoder for an assembly plan. Requires a local ffmpeg binary."""
import argparse,json,shutil,subprocess
from pathlib import Path
p=argparse.ArgumentParser(); p.add_argument('plan'); p.add_argument('--out',required=True); p.add_argument('--fps',type=int,default=25); p.add_argument('--width',type=int,default=1080); p.add_argument('--height',type=int,default=1920); a=p.parse_args()
if not shutil.which('ffmpeg'): raise SystemExit('ffmpeg not found; install it or use another encoder adapter')
plan=json.loads(Path(a.plan).read_text()); missing=plan.get('missing',[])
if missing: raise SystemExit('assembly plan blocked; missing shots: '+','.join(missing))
clips=[Path(x['path']) for x in plan['clips']]
out=Path(a.out); out.parent.mkdir(parents=True,exist_ok=True); concat=out.parent/'concat.txt'; concat.write_text(''.join("file '"+str(p.resolve()).replace("'","'\\''")+"'\n" for p in clips))
cmd=['ffmpeg','-y','-f','concat','-safe','0','-i',str(concat),'-vf',f'scale={a.width}:{a.height}:force_original_aspect_ratio=increase,crop={a.width}:{a.height},setsar=1,fps={a.fps},format=yuv420p','-c:v','libx264','-preset','ultrafast','-c:a','aac','-ar','48000','-ac','2',str(out)]
subprocess.run(cmd,check=True); print(out)
