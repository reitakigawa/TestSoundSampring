"""oto.ini generation from aligned mora segments."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from alias import make_alias
from settings import DEFAULT_BLANK_MS, DEFAULT_FIXED_MS, DEFAULT_OVERLAP_MS, DEFAULT_PREUTTERANCE_MS
from whisper_loader import WordSegment


@dataclass(frozen=True)
class OtoEntry:
    wav_name: str
    alias: str
    offset: float
    consonant: float
    cutoff: float
    preutterance: float
    overlap: float

    def to_line(self) -> str:
        return (
            f"{self.wav_name}={self.alias},{self.offset:.3f},{self.consonant:.3f},"
            f"{self.cutoff:.3f},{self.preutterance:.3f},{self.overlap:.3f}"
        )


def generate_oto_entries(wav_name: str, segments: list[WordSegment]) -> list[OtoEntry]:
    """Generate continuous-sound oto entries by distributing word time over morae."""
    entries: list[OtoEntry] = []
    previous: str | None = None
    for segment in segments:
        if segment.missing:
            previous = None
            continue
        duration_ms = max((segment.end - segment.start) * 1000.0, 1.0)
        mora_duration = duration_ms / max(len(segment.morae), 1)
        for index, current in enumerate(segment.morae):
            start_ms = segment.start * 1000.0 + index * mora_duration
            alias = make_alias(previous, current, start_of_phrase=previous is None)
            cutoff = -(max(mora_duration - DEFAULT_BLANK_MS, 10.0))
            entries.append(
                OtoEntry(
                    wav_name=wav_name,
                    alias=alias,
                    offset=max(start_ms - DEFAULT_OVERLAP_MS, 0.0),
                    consonant=min(DEFAULT_FIXED_MS, mora_duration),
                    cutoff=cutoff,
                    preutterance=min(DEFAULT_PREUTTERANCE_MS, mora_duration / 2),
                    overlap=min(DEFAULT_OVERLAP_MS, mora_duration / 3),
                )
            )
            previous = current
    return entries


def write_oto_ini(path: str | Path, entries: list[OtoEntry]) -> None:
    Path(path).write_text("\n".join(entry.to_line() for entry in entries) + "\n", encoding="utf-8")
