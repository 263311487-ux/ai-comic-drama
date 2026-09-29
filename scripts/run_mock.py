#!/usr/bin/env python3
import argparse,json,sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ai_comic_drama.providers import MockProvider
from ai_comic_drama.runner import run_manifest,BudgetExceeded
p=argparse.ArgumentParser(); p.add_argument('manifest'); p.add_argument('--state',default='work/run_state.json'); p.add_argument('--fail-shot',action='append',default=[]); p.add_argument('--dry-run',action='store_true'); a=p.parse_args()
m=json.loads(Path(a.manifest).read_text())
try: print(json.dumps(run_manifest(m,MockProvider(a.fail_shot),a.state,dry_run=a.dry_run),ensure_ascii=False,indent=2))
except BudgetExceeded as e: print('BLOCKED:',e); raise SystemExit(2)
