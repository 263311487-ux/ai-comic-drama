import json, tempfile, unittest
from pathlib import Path
from ai_comic_drama.providers import MockProvider
from ai_comic_drama.runner import run_manifest
ROOT=Path(__file__).parents[1]
class Runner(unittest.TestCase):
 def setUp(self): self.m=json.loads((ROOT/'examples/episode.json').read_text())
 def test_dry_run(self):
  with tempfile.TemporaryDirectory() as d: self.assertEqual(run_manifest(self.m,MockProvider(),Path(d)/'s.json',dry_run=True)['status'],'dry-run')
 def test_resume(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'s.json'; a=run_manifest(self.m,MockProvider(),p); b=run_manifest(self.m,MockProvider(),p); self.assertEqual(a['attempts'],2); self.assertEqual(b['attempts'],2); self.assertEqual(b['status'],'succeeded')
 def test_failed_shot_review(self):
  with tempfile.TemporaryDirectory() as d:
   s=run_manifest(self.m,MockProvider(['S02']),Path(d)/'s.json'); self.assertEqual(s['status'],'needs-review'); self.assertEqual(s['shots']['S02']['status'],'failed')
