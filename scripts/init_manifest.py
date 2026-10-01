#!/usr/bin/env python3
"""Create a small, valid manifest starter for a new episode."""
import argparse, json
from pathlib import Path

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',required=True); p.add_argument('--title',default='New Episode'); p.add_argument('--episode-id',default='episode-01')
    a=p.parse_args(); out=Path(a.out)
    data={'schema_version':'0.1','episode_id':a.episode_id,'title':a.title,'language':'zh-CN','ratio':'9:16','release_metadata':{'platform':'','ai_disclosure':'AI-generated media; human review required','copyright_basis':'','cover':'','description':''},'delivery':{'width':1080,'height':1920,'fps':25,'audio':True,'subtitles':True},'provider':{'name':'mock','model':'offline-preview','mode':'dry-run'},'budget':{'max_attempts':12,'max_shot_attempts':2},'assets':{'characters':[],'scenes':[]},'shots':[{'id':'S01','duration':5,'purpose':'','action':'','camera':'','end_state':''}]}
    out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n'); print(out)
if __name__=='__main__': main()
