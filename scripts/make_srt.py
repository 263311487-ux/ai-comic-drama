#!/usr/bin/env python3
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from ai_comic_drama.subtitles import srt_for_manifest
p=argparse.ArgumentParser(); p.add_argument('manifest'); p.add_argument('--out',required=True); a=p.parse_args(); m=json.loads(Path(a.manifest).read_text()); out=Path(a.out); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(srt_for_manifest(m),encoding='utf-8'); print(out)
