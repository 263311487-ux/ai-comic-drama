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
    if json.loads(content_qa.read_text(encoding="utf-8")).get("publish_approval") is not True:
        raise SystemExit("缺少人工发布批准；只能标记 TECHNICAL_READY")
    cfg = json.loads(man.read_text(encoding="utf-8"))
    srt = video.parent / "制作成果" / "subs" / f"{cfg.get('title','episode')}_EP{cfg.get('episode','01')}.srt"
    files = [{"path": str(video), "sha256": sha(video)}]
    if not srt.exists(): raise SystemExit("字幕文件缺失，禁止生成交付清单")
    files.append({"path": str(srt), "sha256": sha(srt)})
    result = {"status": "READY_FOR_PUBLISH", "title": cfg.get("title"), "episode": cfg.get("episode", "01"), "manifest": str(man), "created_at": int(time.time()), "files": files, "quality_gates": {"technical": "PASS", "content": "PASS", "compliance": "PASS", "human_publish_approval": "PASS"}}
    out = Path(args.out); out = out if out.is_absolute() else video.parent / out
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(out)

if __name__ == "__main__": main()
