#!/usr/bin/env python3
"""Run the safe, offline first-success workflow and write an artifact index."""
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def run(*args):
    subprocess.run([sys.executable, *args], cwd=ROOT, check=True)

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("manifest", nargs="?", default="examples/episode.json")
    ap.add_argument("--out", default="work/quickstart")
    args = ap.parse_args()
    manifest = Path(args.manifest).resolve()
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    run(str(ROOT / "scripts/validate_manifest.py"), str(manifest))
    run(str(ROOT / "scripts/previz.py"), str(manifest), "--out", str(out / "previz.html"))
    run(str(ROOT / "scripts/qa_report.py"), "--manifest", str(manifest), "--out", str(out / "qa_result.json"))
    run(str(ROOT / "scripts/make_srt.py"), str(manifest), "--out", str(out / "episode.srt"))
    run(str(ROOT / "scripts/assemble_plan.py"), str(manifest), "--out", str(out / "assembly.json"))
    state = out / "run_state.json"
    mock = subprocess.run([sys.executable, str(ROOT / "scripts/run_mock.py"), str(manifest), "--state", str(state)], cwd=ROOT, capture_output=True, text=True, check=True)
    (out / "mock_result.json").write_text(mock.stdout, encoding="utf-8")
    artifacts = {
        "status": "READY_FOR_PROVIDER_REVIEW",
        "manifest": str(manifest),
        "out": str(out),
        "artifacts": {p.name: str(p) for p in sorted(out.iterdir()) if p.is_file()},
        "next": "Review qa_result.json, then choose an explicitly approved provider adapter.",
    }
    index = out / "quickstart.json"
    artifacts["artifacts"][index.name] = str(index)
    index.write_text(json.dumps(artifacts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(artifacts, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
