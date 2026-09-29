#!/usr/bin/env python3
"""成片成本/时长预估：烧钱前先算总账。

用法:
    python3 estimate_cost.py                          # 只报镜头数/总时长
    python3 estimate_cost.py --rate 0.5               # 按 X 元/秒 估算视频成本
    python3 estimate_cost.py --manifest ep01_manifest.json

说明:
    本脚本不内置任何厂商单价（价格会变，写死会误导）。--rate 需要你自查
    Ark/火山当季价格后传入；关键帧成本同理按「镜头数 x 单张单价」自行乘。
"""
import argparse, json
from pathlib import Path


def find_manifest(workdir):
    m = workdir / "manifest.json"
    if m.exists():
        return m
    for p in sorted(workdir.glob("ep*_manifest.json")):
        return p
    raise SystemExit("未找到 manifest.json / ep*_manifest.json")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest")
    ap.add_argument("--workdir", default=".")
    ap.add_argument("--rate", type=float, default=None,
                    help="视频单价（元/秒），不传只报时长")
    ap.add_argument("--pass-rate", type=float, default=1.0,
                    help="实测一次生成通过率 0-1，用于摊废片重出成本")
    ap.add_argument("--versions", type=int, default=1,
                    help="每镜抽卡版本数（seed-n），视频成本按版本数乘")
    ap.add_argument("--keyframe-cost", type=float, default=None,
                    help="Seedream 关键帧单价（元/张）")
    ap.add_argument("--tts-cost", type=float, default=None,
                    help="TTS 单价（元/条对白镜）")
    args = ap.parse_args()
    workdir = Path(args.workdir).resolve()
    man = Path(args.manifest).resolve() if args.manifest else find_manifest(workdir)
    cfg = json.load(open(man, encoding="utf-8"))
    shots = cfg.get("shots", [])

    total = 0.0
    for s in shots:
        total += float(s.get("dur", s.get("duration", 0)))

    n_voice = sum(1 for s in shots if s.get("text"))
    n_refs = sum(1 for s in shots if s.get("roles"))
    print(f"片名: {cfg.get('title', '(未命名)')}", flush=True)
    print(f"镜头数: {len(shots)}", flush=True)
    print(f"总时长: {total:.0f} 秒（约 {total / 60:.1f} 分钟）", flush=True)
    print(f"对白镜: {n_voice} / 参考图镜: {n_refs}", flush=True)
    pass_rate = max(0.01, min(1.0, args.pass_rate))
    versions = max(1, args.versions)
    if args.rate is not None:
        video_cost = total * args.rate * versions / pass_rate
        print(f"视频成本估算: {total:.0f}s x {args.rate} 元/s x {versions}版 / {pass_rate:.0%}通过率 = {video_cost:.2f} 元", flush=True)
        total_cost = video_cost
        if args.keyframe_cost is not None:
            kc = len(shots) * args.keyframe_cost
            total_cost += kc
            print(f"关键帧成本: {len(shots)} 镜 x {args.keyframe_cost} 元 = {kc:.2f} 元", flush=True)
        if args.tts_cost is not None:
            tc = n_voice * args.tts_cost
            total_cost += tc
            print(f"TTS 成本: {n_voice} 条 x {args.tts_cost} 元 = {tc:.2f} 元", flush=True)
        print(f"单集合计(不含资产四视图/修复): {total_cost:.2f} 元", flush=True)
        print("  (角色四视图、fix/extend 修复另计；先小批量实测 pass-rate 再反推)", flush=True)
    else:
        print("提示: 传 --rate <元/秒> 可估算视频成本（单价请自查当季价格）", flush=True)
        print("      加 --pass-rate <0-1> 摊废片重出，--versions <n> 摊抽卡", flush=True)


if __name__ == "__main__":
    main()
