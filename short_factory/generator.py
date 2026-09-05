import json
from pathlib import Path

from .ai import GeminiProvider
from .audio import make_frequency_audio
from .captions import make_ass
from .presets import FREQUENCY_PRESETS, THEME_PRESETS
from .quality import score_brief
from .tts import generate_tts
from .visuals import fallback_visual
from .video import render_short


class ShortFactory:
    def __init__(self, config):
        self.config = config
        self.ai = GeminiProvider(config)

    def _brief(self, frequency, theme, duration, language, variant):
        p = FREQUENCY_PRESETS[frequency]
        theme_text = THEME_PRESETS[theme]
        prompt = f"""
Create one premium YouTube Short creative brief for SynchroVault.
Frequency: {frequency} Hz. Frequency angle: {p['angle']}.
Theme: {theme}: {theme_text}.
Duration: {duration} seconds. Language: {language}. Variant: {variant}.
Brand direction: cinematic, elegant, mysterious, premium. No people.
Do not make medical claims or guarantee financial/health outcomes.
The first 1-2 seconds must create curiosity. Build a clear emotional arc.
The final sentence must naturally connect back to the opening for a loop.
Return JSON only with keys: title, hook, narration, on_screen_text, visual_prompt, description, hashtags.
Narration should be short enough for the requested duration and use natural spoken language.
Visual prompt should describe a vertical cinematic scene, strong depth, controlled highlights, no text, no logo, no watermark.
"""
        result = self.ai.generate_content(prompt)
        if result:
            return result
        return {
            "title": f"{frequency} Hz — {theme}",
            "hook": f"What if the reset starts before you notice it?",
            "narration": f"Take a quiet moment for {theme.lower()}. Let the sound create space to slow down, breathe, and reset. Then notice what changes when you return to the beginning.",
            "on_screen_text": f"{frequency} Hz\n{theme}",
            "visual_prompt": f"Vertical cinematic {p['visual']}, luminous particles, deep dimensional atmosphere, premium studio lighting, slow flowing energy, no people, no text.",
            "description": f"A cinematic {frequency} Hz frequency experience by SynchroVault.",
            "hashtags": [f"#{frequency}Hz", "#frequency", "#synchrovault", f"#{theme.lower()}"]
        }

    def generate(self, frequency, theme, duration, language, generate_visual=True, variant=1, use_tts=True):
        out = self.config.output_dir
        slug = f"{frequency}hz_{theme.lower()}_{variant:02d}"
        brief = self._brief(frequency, theme, duration, language, variant)
        image = out / f"{slug}.png"
        frequency_audio = out / f"{slug}_frequency.wav"
        voice_audio = out / f"{slug}_voice.wav"
        mixed_audio = out / f"{slug}_mix.wav"
        captions = out / f"{slug}.ass"
        video = out / f"{slug}.mp4"
        metadata = out / f"{slug}.json"

        p = FREQUENCY_PRESETS[frequency]
        if generate_visual and not self.ai.generate_image(brief["visual_prompt"], image):
            fallback_visual(image, p["palette"], seed=variant)
        elif not generate_visual:
            fallback_visual(image, p["palette"], seed=variant)

        make_frequency_audio(float(frequency), duration, frequency_audio)

        audio_for_video = frequency_audio
        tts_ok = False
        if use_tts:
            try:
                tts_ok = generate_tts(
                    self.ai,
                    brief["narration"],
                    voice_audio,
                    voice="Kore",
                    language="ko-KR" if language == "Korean" else "en-US",
                )
            except Exception:
                tts_ok = False

        # Mixing is intentionally delegated to FFmpeg so the pipeline stays dependency-light.
        if tts_ok:
            import subprocess
            cmd = [
                self.config.ffmpeg_bin, "-y",
                "-i", str(voice_audio), "-i", str(frequency_audio),
                "-filter_complex", "[0:a]volume=1.0[v];[1:a]volume=0.18[f];[v][f]amix=inputs=2:duration=longest:dropout_transition=2,alimiter=limit=0.92",
                "-c:a", "pcm_s16le", str(mixed_audio),
            ]
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            audio_for_video = mixed_audio

        make_ass(brief["narration"], duration, captions)
        quality = score_brief(brief, duration)
        brief["quality"] = quality
        brief["audio"] = {"tts": tts_ok, "frequency_hz": float(frequency)}

        render_short(
            image, audio_for_video, video, duration,
            self.config.ffmpeg_bin, brief["hook"], captions
        )
        metadata.write_text(json.dumps(brief, ensure_ascii=False, indent=2), encoding="utf-8")
        return {
            "title": brief["title"],
            "video_path": video,
            "metadata_path": metadata,
            "brief": brief,
            "quality": quality,
        }
