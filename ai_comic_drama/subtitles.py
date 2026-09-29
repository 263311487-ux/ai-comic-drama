"""Provider-neutral SRT generation from manifest dialogue timing."""
import re

def segments(text, duration, *, start=0.0, speaker="", max_chars=32):
    text=(text or "").replace("\n"," ").strip()
    if not text: return []
    parts=[x.strip() for x in re.split(r"(?<=[。！？….!?])", text) if x.strip()]
    weights=[max(len(x),1) for x in parts]; total=sum(weights); t=float(start); window=max(float(duration),0.1); out=[]
    for i,part in enumerate(parts):
        end=float(start)+window*sum(weights[:i+1])/total
        out.append({"start":round(t,3),"end":round(min(end,float(start)+window),3),"text":part,"speaker":speaker}); t=end
    return out

def timestamp(seconds):
    seconds=max(0.0,float(seconds)); h=int(seconds//3600); m=int(seconds%3600//60); s=seconds%60
    return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".",",")

def srt_for_manifest(manifest):
    entries=[]; offset=0.0
    for shot in manifest.get("shots",[]):
        entries += segments(shot.get("dialogue") or shot.get("text") or "",shot.get("duration",0),start=offset,speaker=shot.get("speaker") or shot.get("voice") or "")
        offset += float(shot.get("duration",0) or 0)
    lines=[]
    for i,seg in enumerate(entries,1): lines += [str(i),f"{timestamp(seg['start'])} --> {timestamp(seg['end'])}",(seg['speaker']+"：" if seg['speaker'] else "")+seg['text'],""]
    return "\n".join(lines)
