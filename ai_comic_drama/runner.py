"""Resumable, budget-aware shot runner."""
from pathlib import Path
import json, time
from .providers import Provider, json_job

class BudgetExceeded(RuntimeError): pass

def run_manifest(manifest, provider: Provider, state_path, *, dry_run=False):
    path = Path(state_path)
    state = json.loads(path.read_text()) if path.exists() else {"status":"pending","attempts":0,"shots":{},"events":[]}
    budget = manifest.get("budget", {})
    max_attempts = int(budget.get("max_attempts", 0))
    max_shot_attempts = int(budget.get("max_shot_attempts", 1))
    if dry_run: return {"status":"dry-run","estimate":provider.estimate(manifest),"state":state}
    for shot in manifest.get("shots", []):
        sid = shot["id"]
        existing = state["shots"].get(sid)
        if existing and existing.get("status") == "succeeded": continue
        attempts = int(existing.get("attempts", 0)) if existing else 0
        if attempts >= max_shot_attempts: state["shots"][sid] = {"status":"blocked","attempts":attempts,"reason":"shot retry budget exhausted"}; continue
        if max_attempts and state["attempts"] >= max_attempts: raise BudgetExceeded("episode attempt budget exhausted")
        run_id = f"run-{int(time.time())}-{sid}-{attempts+1}"
        job = provider.submit_shot(shot, run_id)
        state["attempts"] += 1; state["shots"][sid] = {"status":job.status,"attempts":attempts+1,"job":json_job(job)}
        state["events"].append({"event":"shot_submitted","run_id":run_id,"shot_id":sid,"job":json_job(job)})
        path.parent.mkdir(parents=True, exist_ok=True); path.write_text(json.dumps(state, ensure_ascii=False, indent=2))
    state["status"] = "succeeded" if all(x.get("status")=="succeeded" for x in state["shots"].values()) else "needs-review"
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2)); return state
