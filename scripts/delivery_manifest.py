#!/usr/bin/env python3
"""Write a traceable delivery manifest only after deterministic QA passes."""
import argparse, hashlib, json, subprocess, time
from pathlib import Path

def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""): h.update(block)
    return h.hexdigest()

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--video", required=True); ap.add_argument("--manifest", required=True); ap.add_argument("--qa", required=True); ap.add_argument("--out", default="delivery_manifest.json"); args = ap.parse_args()
    video, man, qa = map(lambda x: Path(x).resolve(), (args.video, args.manifest, args.qa))
    q = json.loads(qa.read_text(encoding="utf-8"))
    if q.get("status") != "PASS": raise SystemExit("technical QA 未通过，禁止生成交付清单")
    compliance = qa.parent / "compliance_result.json"
    if not compliance.exists() or json.loads(compliance.read_text(encoding="utf-8")).get("status") != "PASS":
        raise SystemExit("合规预检未通过或缺失，禁止生成交付清单")
    content_qa = qa.parent / "qa_result.json"
    if not content_qa.exists() or json.loads(content_qa.read_text(encoding="utf-8")).get("status") != "PASS":
        raise SystemExit("内容审片未通过或缺失，禁止生成交付清单")
    approval_path = qa.parent / "publish_approval.json"
    if not approval_path.exists() or json.loads(approval_path.read_text(encoding="utf-8")).get("status") != "APPROVED":
        raise SystemExit("缺少人工发布批准；只能标记 TECHNICAL_READY")
    approval = json.loads(approval_path.read_text(encoding="utf-8"))
    if approval.get("qa_sha256") != sha(content_qa):
        raise SystemExit("内容报告已更改，批准失效")
    cfg = json.loads(man.read_text(encoding="utf-8"))
    metadata = cfg.get("release_metadata") or {}
    required = {"platform", "ai_disclosure", "copyright_basis", "cover", "description"}
    missing = sorted(k for k in required if not metadata.get(k))
    if missing: raise SystemExit("发布元数据缺失：" + ",".join(missing))
    srt = video.parent / "制作成果" / "subs" / f"{cfg.get('title','episode')}_EP{cfg.get('episode','01')}.srt"
    files = [{"path": str(video), "sha256": sha(video)}]
    if not srt.exists(): raise SystemExit("字幕文件缺失，禁止生成交付清单")
    files.append({"path": str(srt), "sha256": sha(srt)})
    result = {"status": "READY_FOR_PUBLISH", "title": cfg.get("title"), "episode": cfg.get("episode", "01"), "manifest": str(man), "release_metadata": metadata, "approval": json.loads(approval_path.read_text(encoding="utf-8")), "created_at": int(time.time()), "files": files, "quality_gates": {"technical": "PASS", "content": "PASS", "compliance": "PASS", "human_publish_approval": "PASS"}}
    out = Path(args.out); out = out if out.is_absolute() else video.parent / out
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(out)

if __name__ == "__main__": main()
