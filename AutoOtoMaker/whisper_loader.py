"""WhisperX JSON loading and normalization."""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any

from kana import to_hiragana
from mora import split_mora


@dataclass
class WordSegment:
    text: str
    start: float
    end: float
    reading: str = ""
    morae: list[str] = field(default_factory=list)
    missing: bool = False

    def refresh_reading(self) -> None:
        self.reading = to_hiragana(self.reading or self.text)
        self.morae = split_mora(self.reading)
        self.missing = self.start < 0 or self.end <= self.start or not self.morae


def _iter_words(data: dict[str, Any]) -> list[dict[str, Any]]:
    words: list[dict[str, Any]] = []
    for segment in data.get("segments", []):
        if segment.get("words"):
            words.extend(segment["words"])
        elif segment.get("text"):
            words.append({"word": segment["text"], "start": segment.get("start"), "end": segment.get("end")})
    return words


def load_whisperx_json(path: str | Path) -> list[WordSegment]:
    """Load WhisperX JSON and return editable word segments."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    segments: list[WordSegment] = []
    for word in _iter_words(data):
        text = str(word.get("word") or word.get("text") or "").strip()
        start = float(word.get("start", -1) if word.get("start") is not None else -1)
        end = float(word.get("end", -1) if word.get("end") is not None else -1)
        segment = WordSegment(text=text, start=start, end=end)
        segment.refresh_reading()
        segments.append(segment)
    return segments
