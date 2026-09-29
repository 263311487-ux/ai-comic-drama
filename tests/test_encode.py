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
