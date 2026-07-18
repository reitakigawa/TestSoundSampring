"""Audio inspection helpers for single WAV files."""

from __future__ import annotations

from pathlib import Path
import wave

from settings import SILENCE_PEAK_THRESHOLD


def wav_peak(path: str | Path) -> float:
    """Return normalized peak amplitude for 16-bit PCM WAV, or 0 for unreadable/silent files."""
    try:
        with wave.open(str(path), "rb") as wav:
            if wav.getsampwidth() != 2:
                return 0.0
            raw = wav.readframes(wav.getnframes())
    except (wave.Error, OSError, EOFError):
        return 0.0
    if not raw:
        return 0.0
    import array

    samples = array.array("h")
    samples.frombytes(raw)
    if not samples:
        return 0.0
    return max(abs(sample) for sample in samples) / 32768.0


def is_unvoiced(path: str | Path) -> bool:
    """Treat very quiet or unreadable WAV files as not uttered."""
    return wav_peak(path) < SILENCE_PEAK_THRESHOLD
