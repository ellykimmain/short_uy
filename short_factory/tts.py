from pathlib import Path
import base64
import wave


def _write_pcm_wav(path: Path, pcm: bytes, rate: int = 24000) -> Path:
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(rate)
        wf.writeframes(pcm)
    return path


def generate_tts(provider, text: str, output: Path, voice: str = "Kore") -> bool:
    """Generate narration with Gemini TTS. Returns False when no API client is configured."""
    if not provider.client or not text.strip():
        return False

    from google.genai import types

    response = provider.client.models.generate_content(
        model=provider.config.tts_model,
        contents=f"Speak naturally, calmly and clearly at a medium-slow pace. Premium cinematic narration.\n\n{text}",
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name=voice,
                    )
                )
            ),
        ),
    )

    try:
        data = response.candidates[0].content.parts[0].inline_data.data
    except (AttributeError, IndexError, TypeError):
        return False

    if isinstance(data, str):
        data = base64.b64decode(data)
    _write_pcm_wav(output, data)
    return True
