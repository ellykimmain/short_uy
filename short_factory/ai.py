import json
import re
from pathlib import Path

from .config import Config


class GeminiProvider:
    def __init__(self, config: Config):
        self.config = config
        self.client = None
        if config.gemini_api_key:
            from google import genai
            self.client = genai.Client(api_key=config.gemini_api_key)

    def generate_content(self, prompt: str) -> dict:
        if not self.client:
            return {}
        response = self.client.models.generate_content(
            model=self.config.text_model,
            contents=prompt,
        )
        text = getattr(response, "text", "") or ""
        match = re.search(r"\{.*\}", text, re.S)
        if not match:
            raise ValueError("Gemini returned no JSON object")
        return json.loads(match.group(0))

    def generate_image(self, prompt: str, output_path: Path) -> bool:
        if not self.client:
            return False
        from google.genai import types
        response = self.client.models.generate_content(
            model=self.config.image_model,
            contents=[prompt],
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                response_format={"image": {"aspect_ratio": "9:16", "image_size": "1K"}},
            ),
        )
        for part in getattr(response, "parts", []):
            if getattr(part, "inline_data", None) is not None:
                part.as_image().save(output_path)
                return True
        return False
