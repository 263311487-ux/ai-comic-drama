#!/usr/bin/env python3
"""Summarize an episode manifest for production review."""
import argparse, json
from pathlib import Path
def main():
 p=argparse.ArgumentParser(description=__doc__); p.add_argument('manifest'); p.add_argument('--json',action='store_true'); a=p.parse_args(); d=json.loads(Path(a.manifest).read_text(encoding='utf-8')); shots=d.get('shots',[])
 r={'episode_id':d.get('episode_id'),'title':d.get('title'),'shots':len(shots),'duration_seconds':sum(float(s.get('duration',0)) for s in shots),'dialogue_shots':sum(bool(s.get('dialogue') or s.get('text')) for s in shots),'characters':len(d.get('assets',{}).get('characters',[])),'scenes':len(d.get('assets',{}).get('scenes',[])),'ratio':d.get('ratio'),'delivery':d.get('delivery',{}),'provider':d.get('provider',{}),'budget':d.get('budget',{})}
 if a.json: print(json.dumps(r,ensure_ascii=False,indent=2))
 else: print(f"{r['title']} ({r['episode_id']})\nshots: {r['shots']} | duration: {r['duration_seconds']:.1f}s | dialogue: {r['dialogue_shots']}\nassets: {r['characters']} characters, {r['scenes']} scenes | ratio: {r['ratio']}\nprovider: {r['provider'].get('name','unknown')} | max attempts: {r['budget'].get('max_attempts','unset')}")
if __name__=='__main__': main()
