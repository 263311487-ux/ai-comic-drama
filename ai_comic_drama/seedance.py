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
        task_id=""
        try: task_id=json.loads(proc.stdout).get("task_id","")
        except json.JSONDecodeError: pass
        return Job(shot["id"],task_id or f"seedance-{run_id}",status,self.name,evidence)
    def poll(self, job_id):
        proc=subprocess.run([self.binary,"status",job_id,"--json"],capture_output=True,text=True,check=False)
        evidence={"returncode":proc.returncode,"stdout":proc.stdout[-2000:],"stderr":proc.stderr[-2000:]}
        return Job("unknown",job_id,"running" if proc.returncode==0 else "failed",self.name,evidence)
