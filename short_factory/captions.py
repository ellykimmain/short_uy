from pathlib import Path
import re


def _ass_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    cs = int(round((seconds - int(seconds)) * 100))
    if cs >= 100:
        s += 1
        cs = 0
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def make_ass(narration: str, duration: float, output: Path, font_size: int = 64) -> Path:
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", narration.strip()) if s.strip()]
    if not sentences:
        sentences = [narration.strip()]
    weights = [max(1, len(s)) for s in sentences]
    total = sum(weights)
    t = 0.0
    events = []
    for i, sentence in enumerate(sentences):
        span = duration * weights[i] / total
        end = duration if i == len(sentences) - 1 else min(duration, t + span)
        text = sentence.replace("{", "\\{").replace("}", "\\}")
        events.append(f"Dialogue: 0,{_ass_time(t)},{_ass_time(end)},Default,,0,0,0,,{text}")
        t = end

    content = f"""[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\nScaledBorderAndShadow: yes\n\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\nStyle: Default,Arial,{font_size},&H00FFFFFF,&H00FFFFFF,&H80000000,&H55000000,1,0,0,0,100,100,0,0,1,4,1,2,70,70,180,1\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n""" + "\n".join(events) + "\n"
    output.write_text(content, encoding="utf-8")
    return output
