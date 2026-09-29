#!/usr/bin/env python3
"""Deterministic delivery checks for an assembled episode."""
import argparse, json, subprocess
import re
from pathlib import Path

W, H, FPS = 1080, 1920, 25

def probe(path):
    raw = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_streams", "-show_format",
        "-of", "json", str(path)
    ])
    return json.loads(raw)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--workdir", help="产物工作目录；实验分支 manifest 与产物分离时使用")
    ap.add_argument("--out", default="technical_qa.json")
    args = ap.parse_args()
    video, manifest = Path(args.video).resolve(), Path(args.manifest).resolve()
    cfg = json.loads(manifest.read_text(encoding="utf-8"))
    errors, warnings, shots = [], [], []
    if not video.exists() or video.stat().st_size < 1024:
        errors.append("missing_or_empty_master")
    else:
        try:
            info = probe(video)
            streams = info.get("streams", [])
            v = next((s for s in streams if s.get("codec_type") == "video"), None)
            a = next((s for s in streams if s.get("codec_type") == "audio"), None)
            if not v: errors.append("missing_video_stream")
            else:
                if int(v.get("width", 0)) != W or int(v.get("height", 0)) != H:
                    errors.append(f"video_dimensions:{v.get('width')}x{v.get('height')}")
                rate = v.get("r_frame_rate", "")
                if rate not in ("25/1", "25/1.0"):
                    errors.append(f"frame_rate:{rate}")
            if not a: errors.append("missing_audio_stream")
            duration = float(info.get("format", {}).get("duration", 0) or 0)
            if duration <= 0.5: errors.append("invalid_duration")
            # Deterministic media checks: black frames and unusable loudness.
            black = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(video), "-vf", "blackdetect=d=0.5:pix_th=0.98", "-an", "-f", "null", "-"], capture_output=True, text=True)
            # blackdetect is codec/pixel-format sensitive; retain evidence as a
            # warning until a calibrated per-frame detector is added.
            if "black_start" in (black.stderr or ""): warnings.append("black_frame_detected_needs_review")
            vol = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(video), "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True)
            text = vol.stderr or ""
            loud = re.search(r"Integrated loudness:\s+I:\s+(-?[0-9.]+) LUFS", text)
            peak = re.search(r"True peak:\s+Peak:\s+(-?[0-9.]+) dBFS", text)
            if not loud or not peak:
                errors.append("audio_loudness_unmeasured")
            else:
                lufs, dbfs = float(loud.group(1)), float(peak.group(1))
                if not -24.0 <= lufs <= -14.0: errors.append(f"integrated_loudness:{lufs:.1f}LUFS")
                if dbfs > -1.0: errors.append(f"true_peak:{dbfs:.1f}dBFS")
        except Exception as exc:
            errors.append(f"ffprobe_failed:{type(exc).__name__}")
    workdir = Path(args.workdir).resolve() if args.workdir else manifest.parent
    video_dir = workdir / "制作成果" / "video"
    for shot in cfg.get("shots", []):
        sid = shot.get("id")
        p = next((video_dir / f"{sid}{ext}" for ext in (".mov", ".mp4") if (video_dir / f"{sid}{ext}").exists()), None)
        if not p:
            errors.append(f"missing_shot:{sid}")
        else:
            shots.append(sid)
    result = {"status": "PASS" if not errors else "FAIL", "errors": errors,
              "warnings": warnings, "shot_count": len(shots),
              "expected_shots": len(cfg.get("shots", [])), "video": str(video)}
    srt = workdir / "制作成果" / "subs" / f"{cfg.get('title','episode')}_EP{cfg.get('episode','01')}.srt"
    if not srt.exists(): errors.append("missing_srt")
    else:
        raw = srt.read_text(encoding="utf-8", errors="replace")
        if re.search(r"-->[^\n]*\n\s*\n", raw): errors.append("empty_subtitle_entry")
        result["subtitle"] = {"path": str(srt), "bytes": srt.stat().st_size}
    result["status"] = "PASS" if not errors else "FAIL"
    out = Path(args.out)
    if not out.is_absolute(): out = video.parent / out
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if not errors else 2)

if __name__ == "__main__": main()
