#!/usr/bin/env python3
import re,sys
from pathlib import Path
def main(p):
 text=Path(p).read_text(); hits=[]
 for label,pat in [('real-person reference','真人脸|real person|celebrity'),('graphic violence','斩首|断肢|gore|beheading'),('sexual content','色情|裸露|explicit sex')]:
  if re.search(pat,text,re.I): hits.append(label)
 if hits: print('REVIEW_REQUIRED:',', '.join(hits)); return 2
 print('PASS: no bundled high-risk keywords; platform review still required'); return 0
if __name__=='__main__': sys.exit(main(sys.argv[1]))
