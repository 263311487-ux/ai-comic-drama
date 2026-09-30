#!/usr/bin/env python3
"""Record an explicit, auditable human publish approval in a QA report."""
import argparse,json,time,hashlib
from pathlib import Path
p=argparse.ArgumentParser(); p.add_argument('--qa',required=True); p.add_argument('--approved-by',required=True); p.add_argument('--basis',required=True); a=p.parse_args()
path=Path(a.qa); data=json.loads(path.read_text(encoding='utf-8'))
if data.get('status')!='PASS': raise SystemExit('content QA must be PASS before approval')
if not a.approved_by.strip() or not a.basis.strip(): raise SystemExit('reviewer and basis must be nonempty')
approval={'qa_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'status':'APPROVED','approved_by':a.approved_by,'approved_at':int(time.time()),'basis':a.basis,'content_qa':str(path.resolve())}
out=path.parent/'publish_approval.json'; out.write_text(json.dumps(approval,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print(out)
