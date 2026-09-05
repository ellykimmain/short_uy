# SynchroVault Short Factory

Reusable automation engine for premium YouTube Shorts, starting with frequency content and designed to expand into tarot, astrology, meditation, affirmations, manifestation and other vertical-video formats.

## Pipeline

`Frequency → Creative Brief → Hook/Script → Visual Prompt → AI Image → Frequency Audio → Motion Render → Metadata → MP4`

The architecture separates content strategy from rendering so new Shorts categories can reuse the same factory.

## Project structure

```text
short_uy/
├─ app.py
├─ requirements.txt
├─ short_factory/
│  ├─ ai.py          # Gemini text + image provider
│  ├─ audio.py       # frequency tone generator
│  ├─ config.py      # environment/config
│  ├─ generator.py   # end-to-end orchestration
│  ├─ presets.py     # frequency/theme creative identities
│  ├─ video.py       # FFmpeg renderer
│  └─ visuals.py     # local visual fallback
└─ outputs/
```

## Run

1. Install FFmpeg and make sure `ffmpeg` is on PATH.
2. Create a virtual environment and install `requirements.txt`.
3. Set `GEMINI_API_KEY` when AI generation is desired.
4. Run `streamlit run app.py`.

Optional environment variables:

- `GEMINI_TEXT_MODEL` (default: `gemini-3.8-flash`)
- `GEMINI_IMAGE_MODEL` (default: `gemini-3.1-flash-image`)
- `FFMPEG_BIN` (default: `ffmpeg`)

## Important design decision

Text is generated separately from the image. This keeps hooks/captions editable and avoids relying on image-generation models to render readable Korean/English typography.

This is the foundation layer. Production hardening should add TTS, timed subtitles, multiple visual shots per Short, motion presets, audio mastering, quality scoring, duplicate detection, batch queues and YouTube publishing.
