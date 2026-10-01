#!/usr/bin/env python3
"""Report local capabilities without contacting paid providers."""
import argparse, json, os, shutil, sys
from pathlib import Path

def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--out'); p.add_argument('--workdir',default='work'); a=p.parse_args()
    seed=os.environ.get('SEEDANCE_BIN','seedance')
    work=Path(a.workdir); work.mkdir(parents=True,exist_ok=True)
    writable=os.access(work,os.W_OK)
    checks={'python':{'available':True,'version':sys.version.split()[0]},'ffmpeg':{'available':bool(shutil.which('ffmpeg')),'path':shutil.which('ffmpeg')},'ffprobe':{'available':bool(shutil.which('ffprobe')),'path':shutil.which('ffprobe')},'seedance_cli':{'available':bool(shutil.which(seed)),'binary':seed},'offline_manifest':{'available':(Path(__file__).resolve().parents[1]/'examples/episode.json').exists()},'workdir':{'available':writable,'path':str(work.resolve())}}
    ready=checks['offline_manifest']['available'] and checks['workdir']['available']
    result={'status':'READY_OFFLINE' if ready else 'NOT_READY','paid_provider_calls':False,'checks':checks,'next':'Run scripts/quickstart.py for the offline workflow.'}
    text=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
    if a.out: Path(a.out).parent.mkdir(parents=True,exist_ok=True); Path(a.out).write_text(text,encoding='utf-8')
    print(text,end=''); return 0 if ready else 1
if __name__=='__main__': main()
