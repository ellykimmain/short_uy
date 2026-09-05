import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Config:
    root: Path
    output_dir: Path
    gemini_api_key: str | None
    text_model: str
    image_model: str
    ffmpeg_bin: str


def load_config() -> Config:
    root = Path(__file__).resolve().parents[1]
    output_dir = root / "outputs"
    output_dir.mkdir(exist_ok=True)
    return Config(
        root=root,
        output_dir=output_dir,
        gemini_api_key=os.getenv("GEMINI_API_KEY"),
        text_model=os.getenv("GEMINI_TEXT_MODEL", "gemini-3.8-flash"),
        image_model=os.getenv("GEMINI_IMAGE_MODEL", "gemini-3.1-flash-image"),
        ffmpeg_bin=os.getenv("FFMPEG_BIN", "ffmpeg"),
    )
