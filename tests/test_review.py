import json,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).parents[1]
class Review(unittest.TestCase):
 def test_record_pending(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'qa.json'; subprocess.run([sys.executable,str(ROOT/'scripts/record_content_review.py'),'--out',str(p),'--status','PENDING_HUMAN_REVIEW','--reviewer','reviewer','--basis','not reviewed'],check=True); x=json.loads(p.read_text()); self.assertFalse(x['publish_approval'])
 def test_record_pass(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'qa.json'; subprocess.run([sys.executable,str(ROOT/'scripts/record_content_review.py'),'--out',str(p),'--status','PASS','--reviewer','reviewer','--basis','shot review','--shot','S01'],check=True); self.assertEqual(json.loads(p.read_text())['shots'][0]['status'],'REVIEWED')
 def test_recorded_pass_starts_without_publish_approval(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'qa_result.json'; subprocess.run([sys.executable,str(ROOT/'scripts/record_content_review.py'),'--out',str(p),'--status','PASS','--reviewer','reviewer','--basis','shot review'],check=True)
   self.assertFalse(json.loads(p.read_text())['publish_approval'])
