import subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).parents[1]
def run(*args): return subprocess.run([sys.executable,*args],cwd=ROOT,text=True,capture_output=True)
class Offline(unittest.TestCase):
    def test_manifest(self): self.assertEqual(run("scripts/validate_manifest.py","examples/episode.json").returncode,0)
    def test_compliance(self): self.assertEqual(run("scripts/check_compliance.py","examples/episode.json").returncode,0)
    def test_previz(self):
        with tempfile.TemporaryDirectory() as d: self.assertEqual(run("scripts/previz.py","examples/episode.json","--out",str(Path(d)/"p.html")).returncode,0)
    def test_qa(self):
        with tempfile.TemporaryDirectory() as d: self.assertEqual(run("scripts/qa_report.py","--manifest","examples/episode.json","--out",str(Path(d)/"q.json")).returncode,0)
    def test_srt(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"episode.srt"; self.assertEqual(run("scripts/make_srt.py","examples/episode.json","--out",str(p)).returncode,0); self.assertIn('-->',p.read_text())
    def test_assemble_plan(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"plan.json"; self.assertEqual(run("scripts/assemble_plan.py","examples/episode.json","--out",str(p)).returncode,0); self.assertEqual(__import__('json').loads(p.read_text())['status'],'blocked')
    def test_quickstart(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/"quickstart"; result=run("scripts/quickstart.py","examples/episode.json","--out",str(out))
            self.assertEqual(result.returncode,0, result.stderr)
            data=__import__('json').loads((out/"quickstart.json").read_text())
            self.assertEqual(data["status"],"READY_FOR_PROVIDER_REVIEW")
            self.assertIn("quickstart.json",data["artifacts"])
if __name__=="__main__": unittest.main()
