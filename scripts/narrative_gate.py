#!/usr/bin/env python3
"""Pre-generation narrative comprehensibility gate for an episode manifest."""
import argparse, json, re, sys
from pathlib import Path

REQUIRED = {
    "protagonist": "主角",
    "goal": "目标",
    "obstacle": "阻力",
    "stakes": "代价",
    "turn": "反转",
    "result": "本集结果",
    "cliffhanger": "结尾问题",
}

def text_of(shot):
    return " ".join(str(shot.get(k, "") or "") for k in ("speaker", "text", "img", "motion", "sfx"))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--out")
    args = ap.parse_args()
    path = Path(args.manifest)
    data = json.loads(path.read_text(encoding="utf-8"))
    shots = data.get("shots") or []
    narrative = data.get("narrative_gate") or {}
    all_text = "\n".join(text_of(s) for s in shots)
    checks = []

    for key, label in REQUIRED.items():
        value = str(narrative.get(key, "") or "").strip()
        checks.append({"id": f"N-{key}", "label": label, "ok": bool(value), "detail": value or "manifest 缺少 narrative_gate 字段"})

    # These are deliberately explainable heuristics. They block obvious omissions,
    # while leaving final story judgment to the director review.
    checks += [
        {"id": "N-01", "label": "单集镜头数量", "ok": 5 <= len(shots) <= 30, "detail": f"{len(shots)} 镜"},
        {"id": "N-02", "label": "开场钩子", "ok": bool(shots) and len(text_of(shots[0])) >= 12, "detail": "首镜有可读画面/声音信息" if shots else "无镜头"},
        {"id": "N-03", "label": "前20秒任务建立", "ok": bool(re.search(r"目标|任务|救|找|逃|活|回去|倒计时|必须", "\n".join(text_of(s) for s in shots[:6]))), "detail": "前段出现任务或生存压力"},
        {"id": "N-04", "label": "可见因果动作", "ok": any(s.get("motion") and s.get("text") for s in shots), "detail": "至少一镜同时有动作和对白因果"},
        {"id": "N-05", "label": "结尾悬念", "ok": bool(shots) and bool(re.search(r"下一|还剩|倒计时|将要|是谁|何处|继续|未完|第二|更大", text_of(shots[-1]))), "detail": "末镜包含后续问题或压力" if shots else "无末镜"},
    ]
    failures = [c for c in checks if not c["ok"]]
    report = {"manifest": str(path.resolve()), "status": "FAIL" if failures else "PASS", "checks": checks, "failures": failures,
              "disclaimer": "启发式前置门，不替代导演对样片的最终审片。"}
    out = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(out, encoding="utf-8")
    print(out, end="")
    return 1 if failures else 0

if __name__ == "__main__":
    raise SystemExit(main())
