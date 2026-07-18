"""Waveform loading helpers for GUI display."""

from __future__ import annotations

import wave
from pathlib import Path


def read_waveform(path: str | Path, max_points: int = 2000) -> tuple[list[float], float]:
    """Return normalized mono peak samples and duration seconds from a WAV file."""
    with wave.open(str(path), "rb") as wav:
        frames = wav.getnframes()
        channels = wav.getnchannels()
        width = wav.getsampwidth()
        rate = wav.getframerate()
        raw = wav.readframes(frames)
    if width != 2:
        return [], frames / rate if rate else 0.0
    import array

    samples = array.array("h")
    samples.frombytes(raw)
    if channels > 1:
        samples = array.array("h", samples[::channels])
    stride = max(len(samples) // max_points, 1)
    peaks = [max(abs(v) for v in samples[i : i + stride]) / 32768.0 for i in range(0, len(samples), stride)]
    return peaks, frames / rate if rate else 0.0
