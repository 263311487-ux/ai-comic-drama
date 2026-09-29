#!/usr/bin/env python3
import argparse,json,html
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('manifest');p.add_argument('--out',default='previz.html');a=p.parse_args();d=json.loads(Path(a.manifest).read_text()); rows=''.join('<tr>'+''.join(f'<td>{html.escape(str(s.get(k,"")))}</td>' for k in ['id','duration','purpose','action','camera','end_state'])+'</tr>' for s in d.get('shots',[])); Path(a.out).write_text('<meta charset="utf-8"><h1>'+html.escape(d.get('title','Episode'))+'</h1><table border="1"><tr><th>ID</th><th>Sec</th><th>Purpose</th><th>Action</th><th>Camera</th><th>End</th></tr>'+rows+'</table>');print('WROTE',a.out)
