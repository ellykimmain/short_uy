from pathlib import Path
import subprocess


def render_short(image: Path, audio: Path, output: Path, duration: int, ffmpeg_bin: str = "ffmpeg", hook: str = "") -> Path:
    # Text is intentionally kept out of the generated image. FFmpeg overlays it so it remains readable and editable.
    drawtext = (
        f"drawtext=text='{hook.replace(chr(39), chr(92)+chr(39))}':"
        "fontcolor=white:fontsize=54:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
        "x=(w-text_w)/2:y=h*0.12:box=1:boxcolor=black@0.35:boxborderw=18"
    )
    vf = f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,{drawtext}"
    cmd = [
        ffmpeg_bin, "-y", "-loop", "1", "-i", str(image), "-i", str(audio),
        "-t", str(duration), "-vf", vf,
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(output)
    ]
    subprocess.run(cmd, check=True, capture_output=True, text=True)
    return output
