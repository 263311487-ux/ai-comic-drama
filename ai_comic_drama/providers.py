"""Small provider contract with an offline implementation.

Real adapters should keep network/auth code outside the core and return these records.
"""
from dataclasses import dataclass, asdict
from typing import Any, Dict, Protocol
import hashlib, json, time

@dataclass
class Job:
    shot_id: str
    job_id: str
    status: str
    provider: str
    evidence: Dict[str, Any]

class Provider(Protocol):
    name: str
    def capabilities(self) -> Dict[str, Any]: ...
    def estimate(self, manifest: Dict[str, Any]) -> Dict[str, Any]: ...
    def submit_shot(self, shot: Dict[str, Any], run_id: str) -> Job: ...
    def poll(self, job_id: str) -> Job: ...

class MockProvider:
    name = "mock"
    def __init__(self, fail_shots=None): self.fail_shots = set(fail_shots or [])
    def capabilities(self):
        return {"ratios": ["9:16", "16:9", "1:1", "21:9"], "audio": False, "offline": True}
    def estimate(self, manifest):
        return {"provider": self.name, "shots": len(manifest.get("shots", [])), "requires_network": False}
    def submit_shot(self, shot, run_id):
        sid = shot["id"]
        digest = hashlib.sha256(f"{run_id}:{sid}".encode()).hexdigest()[:16]
        status = "failed" if sid in self.fail_shots else "succeeded"
        return Job(sid, f"mock-{digest}", status, self.name, {"offline": True, "created_at": time.time()})
    def poll(self, job_id):
        return Job("unknown", job_id, "succeeded", self.name, {"offline": True})

def json_job(job): return asdict(job)
