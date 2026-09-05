from pathlib import Path
import math
import wave

import numpy as np


def make_frequency_audio(frequency: float, duration: int, output_path: Path, sample_rate: int = 44100) -> Path:
    n = int(sample_rate * duration)
    t = np.arange(n, dtype=np.float32) / sample_rate
    # Pure carrier + very low amplitude binaural-style modulation for texture.
    signal = 0.18 * np.sin(2 * math.pi * frequency * t)
    signal += 0.035 * np.sin(2 * math.pi * (frequency / 2) * t)
    fade = np.minimum(1.0, np.minimum(t / 1.5, (duration - t) / 1.5))
    fade = np.clip(fade, 0, 1)
    signal *= fade
    pcm = np.int16(np.clip(signal, -1, 1) * 32767)
    with wave.open(str(output_path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm.tobytes())
    return output_path
