import json,shutil,subprocess,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).parents[1]
class Encode(unittest.TestCase):
 @unittest.skipUnless(shutil.which('ffmpeg'),'ffmpeg unavailable')
 def test_fixture_encode_and_plan(self):
  with tempfile.TemporaryDirectory() as d:
   d=Path(d); shots=d/'shots'; shots.mkdir()
   for sid in ('S01','S02'):
    subprocess.run(['ffmpeg','-y','-loglevel','error','-f','lavfi','-i','color=c=navy:s=270x480:d=1','-f','lavfi','-i','anullsrc=r=48000:cl=stereo','-shortest','-c:v','libx264','-c:a','aac',str(shots/f'{sid}.mp4')],check=True)
   src=json.loads((ROOT/'examples/episode.json').read_text()); src['shots'][0]['duration']=1; src['shots'][1]['duration']=1; manifest=d/'manifest.json'; manifest.write_text(json.dumps(src,ensure_ascii=False)); plan=d/'plan.json'; subprocess.run(['python3',str(ROOT/'scripts/assemble_plan.py'),str(manifest),'--video-dir',str(shots),'--out',str(plan)],check=True)
   self.assertEqual(json.loads(plan.read_text())['status'],'ready'); out=d/'master.mp4'; subprocess.run(['python3',str(ROOT/'scripts/encode_ffmpeg.py'),str(plan),'--out',str(out)],check=True); self.assertGreater(out.stat().st_size,1024)
 @unittest.skipUnless(shutil.which('ffmpeg'),'ffmpeg unavailable')
 def test_offline_delivery(self):
  with tempfile.TemporaryDirectory() as d:
   target=Path(d)/'delivery'; subprocess.run(['python3',str(ROOT/'scripts/offline_delivery.py'),str(ROOT/'examples/episode.json'),'--out',str(target)],check=True)
   report=json.loads((target/'technical_qa.json').read_text()); self.assertEqual(report['status'],'PASS')
 @unittest.skipUnless(shutil.which('ffmpeg'),'ffmpeg unavailable')
 def test_delivery_manifest_requires_publish_approval(self):
  with tempfile.TemporaryDirectory() as d:
   target=Path(d)/'delivery'; subprocess.run(['python3',str(ROOT/'scripts/offline_delivery.py'),str(ROOT/'examples/episode.json'),'--out',str(target)],check=True,stdout=subprocess.DEVNULL)
   (target/'compliance_result.json').write_text(json.dumps({'status':'PASS'}))
   (target/'qa_result.json').write_text(json.dumps({'status':'PASS'}))
   proc=subprocess.run(['python3',str(ROOT/'scripts/delivery_manifest.py'),'--video',str(target/'master.mp4'),'--manifest',str(ROOT/'examples/episode.json'),'--qa',str(target/'technical_qa.json'),'--out',str(target/'delivery.json')],capture_output=True,text=True)
   self.assertNotEqual(proc.returncode,0); self.assertIn('人工发布批准',proc.stderr+proc.stdout)
 @unittest.skipUnless(shutil.which('ffmpeg'),'ffmpeg unavailable')
 def test_approval_creates_publish_manifest(self):
  with tempfile.TemporaryDirectory() as d:
   target=Path(d)/'delivery'; subprocess.run(['python3',str(ROOT/'scripts/offline_delivery.py'),str(ROOT/'examples/episode.json'),'--out',str(target)],check=True,stdout=subprocess.DEVNULL)
   qa=target/'qa_result.json'; q=json.loads(qa.read_text()); q['status']='PASS'; qa.write_text(json.dumps(q))
   compliance=target/'compliance_result.json'; compliance.write_text(json.dumps({'status':'PASS','source':'test-only explicit override'}))
   subprocess.run(['python3',str(ROOT/'scripts/approve_publish.py'),'--qa',str(target/'qa_result.json'),'--approved-by','test-reviewer','--basis','offline fixture review'],check=True)
   out=target/'delivery.json'; subprocess.run(['python3',str(ROOT/'scripts/delivery_manifest.py'),'--video',str(target/'master.mp4'),'--manifest',str(ROOT/'examples/episode.json'),'--qa',str(target/'technical_qa.json'),'--out',str(out)],check=True)
   self.assertEqual(json.loads(out.read_text())['status'],'READY_FOR_PUBLISH')
