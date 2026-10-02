import subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).parents[1]
def run(*args): return subprocess.run([sys.executable,*args],cwd=ROOT,text=True,capture_output=True)
class Offline(unittest.TestCase):
    def test_manifest(self): self.assertEqual(run("scripts/validate_manifest.py","examples/episode.json").returncode,0)
    def test_manifest_strict(self): self.assertEqual(run("scripts/validate_manifest.py","examples/episode.json","--strict").returncode,0)
    def test_manifest_report(self):
        result=run("scripts/manifest_report.py","examples/episode.json","--json"); self.assertEqual(result.returncode,0)
        data=__import__('json').loads(result.stdout); self.assertEqual(data['shots'],2); self.assertEqual(data['duration_seconds'],11.0)
    def test_continuity_check(self):
        result=run("scripts/continuity_check.py","examples/episode.json","--json"); self.assertEqual(result.returncode,0)
        self.assertEqual(__import__('json').loads(result.stdout)['status'],'PASS')
    def test_continuity_check_reports_missing_source(self):
        import json
        with tempfile.TemporaryDirectory() as d:
            manifest=Path(d)/"broken.json"; data=json.loads(Path(ROOT/"examples/episode.json").read_text()); data['shots'][1]['continuity_from']='S99'; manifest.write_text(json.dumps(data))
            result=run("scripts/continuity_check.py",str(manifest),"--json")
            self.assertEqual(result.returncode,1); report=json.loads(result.stdout); self.assertEqual(report['status'],'FAIL'); self.assertEqual(report['issues'][0]['type'],'missing_continuity_source')
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
    def test_init_manifest_creates_contract(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/"episode.json"; result=run("scripts/init_manifest.py","--out",str(out),"--title","Test Episode")
            self.assertEqual(result.returncode,0, result.stderr)
            self.assertEqual(run("scripts/validate_manifest.py",str(out)).returncode,1)
    def test_doctor_is_offline_and_ready(self):
        result=run("scripts/doctor.py", "--workdir", "work"); self.assertEqual(result.returncode,0, result.stderr)
        data=__import__('json').loads(result.stdout); self.assertEqual(data['status'],'READY_OFFLINE'); self.assertFalse(data['paid_provider_calls'])
if __name__=="__main__": unittest.main()
