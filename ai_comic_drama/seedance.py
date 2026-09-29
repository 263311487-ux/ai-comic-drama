"""Explicit Seedance CLI adapter.

This module never submits work unless the caller opts in with execute=True.
Credentials are resolved by the installed CLI, not read or printed here.
"""
from dataclasses import asdict
from pathlib import Path
import json, os, subprocess
from .providers import Job

class SeedanceCLI:
    name = "seedance-cli"
    def __init__(self, binary=None, *, execute=False):
        self.binary = binary or os.environ.get("SEEDANCE_BIN", "seedance")
        self.execute = execute
    def capabilities(self):
        return {"ratios":["9:16","16:9","1:1","21:9","adaptive"],"models":["standard","fast","2.5"],"audio":True,"requires_cli":True}
    def estimate(self, manifest):
        seconds=sum(float(s.get("duration",0)) for s in manifest.get("shots",[]))
        return {"provider":self.name,"seconds":seconds,"requires_network":True,"execute_opt_in":self.execute}
    def command(self, shot, *, output=None, model="2.5", resolution="720p", audio_gen=False):
        prompt=shot.get("prompt") or shot.get("action") or ""
        cmd=[self.binary,"generate",prompt,"--model",model,"--duration",str(shot.get("duration",5)),"--ratio",shot.get("ratio","9:16"),"--resolution",resolution,"--json"]
        if audio_gen: cmd.append("--audio-gen")
        if output: cmd += ["--wait","--strict","--output",str(output)]
        return cmd
    def submit_shot(self, shot, run_id):
        if not self.execute: return Job(shot["id"],f"dry-{run_id}","blocked",self.name,{"reason":"execute=False; paid/network generation not submitted"})
        cmd=self.command(shot)
        proc=subprocess.run(cmd,capture_output=True,text=True,check=False)
        evidence={"command":cmd,"returncode":proc.returncode,"stdout":proc.stdout[-2000:],"stderr":proc.stderr[-2000:]}
        status="submitted" if proc.returncode==0 else "failed"
        task_id=self.parse_task_id(proc.stdout)
        return Job(shot["id"],task_id or f"seedance-{run_id}",status,self.name,evidence)
    @staticmethod
    def parse_task_id(stdout):
        try:
            data=json.loads(stdout)
        except json.JSONDecodeError:
            return ""
        if isinstance(data, dict):
            return str(data.get("task_id") or data.get("id") or data.get("taskId") or "")
        return ""
    @staticmethod
    def map_status(payload):
        raw=str(payload.get("status") or payload.get("state") or "").lower()
        if raw in {"succeeded","success","completed","done"}: return "succeeded"
        if raw in {"failed","error","cancelled","canceled"}: return "failed"
        if raw in {"queued","pending","running","processing","submitted"}: return "running"
        return "unknown"
    def poll(self, job_id):
        proc=subprocess.run([self.binary,"status",job_id,"--json"],capture_output=True,text=True,check=False)
        evidence={"returncode":proc.returncode,"stdout":proc.stdout[-2000:],"stderr":proc.stderr[-2000:]}
        try: payload=json.loads(proc.stdout)
        except json.JSONDecodeError: payload={}
        return Job("unknown",job_id,self.map_status(payload) if proc.returncode==0 else "failed",self.name,evidence)
    def download(self, job_id, output):
        output=Path(output); output.parent.mkdir(parents=True, exist_ok=True)
        proc=subprocess.run([self.binary,"download",job_id,"--output",str(output)],capture_output=True,text=True,check=False)
        ok=proc.returncode==0 and output.exists() and output.stat().st_size>10240
        return {"status":"succeeded" if ok else "failed","path":str(output),"bytes":output.stat().st_size if output.exists() else 0,"stdout":proc.stdout[-2000:],"stderr":proc.stderr[-2000:]}
