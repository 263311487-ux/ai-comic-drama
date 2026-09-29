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
if __name__=="__main__": unittest.main()
