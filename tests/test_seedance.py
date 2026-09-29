import json,unittest
from pathlib import Path
from ai_comic_drama.seedance import SeedanceCLI
ROOT=Path(__file__).parents[1]
class Seedance(unittest.TestCase):
 def setUp(self): self.m=json.loads((ROOT/'examples/episode.json').read_text()); self.s=self.m['shots'][0]
 def test_plan_is_network_free(self):
  p=SeedanceCLI(execute=False); self.assertFalse(p.execute); self.assertTrue(p.estimate(self.m)['requires_network'])
 def test_command(self):
  c=SeedanceCLI().command(self.s); self.assertEqual(c[1],'generate'); self.assertIn('--model',c); self.assertNotIn('--wait',c)
 def test_submit_blocked_by_default(self):
  j=SeedanceCLI().submit_shot(self.s,'r1'); self.assertEqual(j.status,'blocked')
 def test_parse_task_id_shapes(self):
  self.assertEqual(SeedanceCLI.parse_task_id('{"task_id":"abc"}'),'abc')
  self.assertEqual(SeedanceCLI.parse_task_id('{"id":"xyz"}'),'xyz')
  self.assertEqual(SeedanceCLI.parse_task_id('not-json'),'')
 def test_status_mapping(self):
  self.assertEqual(SeedanceCLI.map_status({'status':'completed'}),'succeeded')
  self.assertEqual(SeedanceCLI.map_status({'state':'processing'}),'running')
  self.assertEqual(SeedanceCLI.map_status({'status':'error'}),'failed')
