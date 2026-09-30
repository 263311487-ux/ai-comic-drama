#!/usr/bin/env python3
"""Run fixture -> plan -> encode -> subtitles -> technical QA offline."""
import argparse,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(); p.add_argument('manifest'); p.add_argument('--out',required=True); a=p.parse_args()
manifest=Path(a.manifest).resolve(); out=Path(a.out).resolve(); out.mkdir(parents=True,exist_ok=True)
def run(*args): subprocess.run([sys.executable,*args],check=True)
run(str(ROOT/'scripts/fixture_episode.py'),'--manifest',str(manifest),'--out',str(out))
shots=out/'制作成果'/'video'; plan=out/'assembly.json'; run(str(ROOT/'scripts/assemble_plan.py'),str(manifest),'--video-dir',str(shots),'--out',str(plan))
master=out/'master.mp4'; run(str(ROOT/'scripts/encode_ffmpeg.py'),str(plan),'--out',str(master))
subs=out/'制作成果'/'subs'; subs.mkdir(parents=True,exist_ok=True); cfg=json.loads(manifest.read_text()); srt=subs/f"{cfg.get('title','episode')}_EP{cfg.get('episode','01')}.srt"; run(str(ROOT/'scripts/make_srt.py'),str(manifest),'--out',str(srt))
(out/'compliance_result.json').write_text(json.dumps({'status':'REVIEW_REQUIRED','source':'offline fixture; not a real platform review'})); (out/'qa_result.json').write_text(json.dumps({'status':'PENDING_HUMAN_REVIEW','review_type':'content','publish_approval':False,'source':'offline fixture'}))
run(str(ROOT/'scripts/technical_qa.py'),'--video',str(master),'--manifest',str(manifest),'--workdir',str(out),'--out',str(out/'technical_qa.json'))
print(out)
