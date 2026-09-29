import subprocess,sys
from pathlib import Path
ROOT=Path(__file__).parents[1]
def run(*args): return subprocess.run([sys.executable,*args],cwd=ROOT,text=True,capture_output=True)
def test_manifest(): assert run('scripts/validate_manifest.py','examples/episode.json').returncode==0
def test_compliance(): assert run('scripts/check_compliance.py','examples/episode.json').returncode==0
def test_previz(tmp_path): assert run('scripts/previz.py','examples/episode.json','--out',str(tmp_path/'p.html')).returncode==0
def test_qa(tmp_path): assert run('scripts/qa_report.py','--manifest','examples/episode.json','--out',str(tmp_path/'q.json')).returncode==0
