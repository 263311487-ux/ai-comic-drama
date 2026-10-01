#!/usr/bin/env python3
"""Report local capabilities without contacting paid providers."""
import argparse, json, os, shutil, sys
from pathlib import Path

def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--out'); a=p.parse_args()
    seed=os.environ.get('SEEDANCE_BIN','seedance')
    checks={'python':{'available':True,'version':sys.version.split()[0]},'ffmpeg':{'available':bool(shutil.which('ffmpeg')),'path':shutil.which('ffmpeg')},'ffprobe':{'available':bool(shutil.which('ffprobe')),'path':shutil.which('ffprobe')},'seedance_cli':{'available':bool(shutil.which(seed)),'binary':seed},'offline_manifest':{'available':(Path(__file__).resolve().parents[1]/'examples/episode.json').exists()}}
    result={'status':'READY_OFFLINE' if checks['offline_manifest']['available'] else 'NOT_READY','paid_provider_calls':False,'checks':checks,'next':'Run scripts/quickstart.py for the offline workflow.'}
    text=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
    if a.out: Path(a.out).parent.mkdir(parents=True,exist_ok=True); Path(a.out).write_text(text,encoding='utf-8')
    print(text,end='')
if __name__=='__main__': main()
