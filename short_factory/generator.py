import json
import random
from pathlib import Path

from .ai import GeminiProvider
from .audio import make_frequency_audio
from .presets import FREQUENCY_PRESETS, THEME_PRESETS
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
Create one premium YouTube Short creative brief.
Frequency: {frequency} Hz. Frequency angle: {p['angle']}.
Theme: {theme}: {theme_text}.
Duration: {duration} seconds. Language: {language}. Variant: {variant}.
Brand: SynchroVault. No people. No medical claims. Avoid guaranteed outcomes.
The first 1-2 seconds must create curiosity. The final line should make a natural loop.
Return JSON only with keys: title, hook, narration, on_screen_text, visual_prompt, description, hashtags.
Keep narration concise enough for the requested duration. Make it premium, cinematic and non-generic.
"""
        result = self.ai.generate_content(prompt)
        if result:
            return result
        return {
            "title": f"{frequency} Hz — {theme}",
            "hook": f"Why does {frequency} Hz feel different?",
            "narration": f"A quiet moment for {theme.lower()}. Let the sound create space to slow down and reset.",
            "on_screen_text": f"{frequency} Hz\n{theme}",
            "visual_prompt": p["visual"],
            "description": f"A cinematic {frequency} Hz frequency Short by SynchroVault.",
            "hashtags": [f"#{frequency}Hz", "#frequency", "#synchrovault", f"#{theme.lower()}"]
        }

    def generate(self, frequency, theme, duration, language, generate_visual=True, variant=1):
        out = self.config.output_dir
        slug = f"{frequency}hz_{theme.lower()}_{variant:02d}"
        brief = self._brief(frequency, theme, duration, language, variant)
        image = out / f"{slug}.png"
        audio = out / f"{slug}.wav"
        video = out / f"{slug}.mp4"
        metadata = out / f"{slug}.json"

        p = FREQUENCY_PRESETS[frequency]
        if generate_visual and not self.ai.generate_image(brief["visual_prompt"], image):
            fallback_visual(image, p["palette"], seed=variant)
        elif not generate_visual:
            fallback_visual(image, p["palette"], seed=variant)

        make_frequency_audio(float(frequency), duration, audio)
        render_short(image, audio, video, duration, self.config.ffmpeg_bin, brief["hook"])
        metadata.write_text(json.dumps(brief, ensure_ascii=False, indent=2), encoding="utf-8")
        return {"title": brief["title"], "video_path": video, "metadata_path": metadata, "brief": brief}
