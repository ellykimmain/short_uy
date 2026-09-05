from pathlib import Path
import subprocess


def _escape_ass(text: str) -> str:
    return (text.replace("\\", "\\\\")
                .replace("{", "\\{")
                .replace("}", "\\}")
                .replace("\n", "\\N"))


def render_short(
    image: Path,
    audio: Path,
    output: Path,
    duration: int,
    ffmpeg_bin: str = "ffmpeg",
    hook: str = "",
    caption_file: Path | None = None,
) -> Path:
    """Render a premium 9:16 Short with subtle camera motion and optional timed captions."""
    filters = [
        "scale=1080:1920:force_original_aspect_ratio=increase",
        "crop=1080:1920",
        # Slow push-in prevents the AI image from feeling like a static slideshow.
        "zoompan=z='min(zoom+0.0007,1.08)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps=30",
        "format=yuv420p",
    ]

    if caption_file and caption_file.exists():
        filters.append(f"ass='{caption_file.as_posix().replace(chr(39), chr(92)+chr(39))}'")
    elif hook:
        filters.append(
            "drawtext="
            f"text='{_escape_ass(hook)}':"
            "fontcolor=white:fontsize=58:"
            "fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
            "x=(w-text_w)/2:y=h*0.12:box=1:boxcolor=black@0.32:boxborderw=18"
        )

    vf = ",".join(filters)
    cmd = [
        ffmpeg_bin, "-y",
        "-loop", "1", "-i", str(image),
        "-i", str(audio),
        "-t", str(duration),
        "-vf", vf,
        "-r", "30",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        "-movflags", "+faststart",
        str(output),
    ]
    subprocess.run(cmd, check=True, capture_output=True, text=True)
    return output
