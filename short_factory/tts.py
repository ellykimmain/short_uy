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


def generate_tts(provider, text: str, output: Path, voice: str = "Kore", language: str = "en-US") -> bool:
    """Generate narration with Gemini TTS. Returns False when no API client is configured."""
    if not provider.client or not text.strip():
        return False
    interaction = provider.client.interactions.create(
        model=provider.config.tts_model,
        input=f"Speak naturally and calmly. Medium-slow pace. Clear premium documentary voice.\n\n{text}",
        response_format={"type": "audio"},
        generation_config={
            "speech_config": [{"voice": voice, "language": language}]
        },
    )
    audio = getattr(interaction, "output_audio", None)
    data = getattr(audio, "data", None) if audio else None
    if not data:
        return False
    if isinstance(data, str):
        data = base64.b64decode(data)
    _write_pcm_wav(output, data)
    return True
