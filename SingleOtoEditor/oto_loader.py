"""Load and save UTAU single-sound oto.ini records."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from settings import DEFAULT_CONSONANT, DEFAULT_CUTOFF, DEFAULT_OFFSET, DEFAULT_OVERLAP, DEFAULT_PREUTTERANCE, OTO_FILE_NAME


@dataclass
class SingleOtoEntry:
    wav_name: str
    alias: str
    offset: float = DEFAULT_OFFSET
    consonant: float = DEFAULT_CONSONANT
    cutoff: float = DEFAULT_CUTOFF
    preutterance: float = DEFAULT_PREUTTERANCE
    overlap: float = DEFAULT_OVERLAP
    missing: bool = False

    @classmethod
    def from_line(cls, line: str) -> "SingleOtoEntry | None":
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            return None
        wav_name, rest = line.split("=", 1)
        parts = [part.strip() for part in rest.split(",")]
        values = parts + [""] * (6 - len(parts))
        return cls(
            wav_name=wav_name.strip(),
            alias=values[0] or Path(wav_name).stem,
            offset=_float_or_default(values[1], DEFAULT_OFFSET),
            consonant=_float_or_default(values[2], DEFAULT_CONSONANT),
            cutoff=_float_or_default(values[3], DEFAULT_CUTOFF),
            preutterance=_float_or_default(values[4], DEFAULT_PREUTTERANCE),
            overlap=_float_or_default(values[5], DEFAULT_OVERLAP),
        )

    def to_line(self) -> str:
        return (
            f"{self.wav_name}={self.alias},{self.offset:.3f},{self.consonant:.3f},"
            f"{self.cutoff:.3f},{self.preutterance:.3f},{self.overlap:.3f}"
        )


def _float_or_default(value: str, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def load_folder(folder: str | Path) -> list[SingleOtoEntry]:
    """Load WAV files and merge any existing oto.ini data in *folder*."""
    folder = Path(folder)
    oto_entries = _read_oto_ini(folder / OTO_FILE_NAME)
    by_wav = {entry.wav_name: entry for entry in oto_entries}
    entries: list[SingleOtoEntry] = []
    for wav_path in sorted(folder.glob("*.wav")):
        entry = by_wav.pop(wav_path.name, SingleOtoEntry(wav_name=wav_path.name, alias=wav_path.stem))
        entries.append(entry)
    for orphan in by_wav.values():
        orphan.missing = True
        entries.append(orphan)
    return entries


def _read_oto_ini(path: Path) -> list[SingleOtoEntry]:
    if not path.exists():
        return []
    entries: list[SingleOtoEntry] = []
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        entry = SingleOtoEntry.from_line(line)
        if entry is not None:
            entries.append(entry)
    return entries


def save_oto_ini(folder: str | Path, entries: list[SingleOtoEntry]) -> None:
    """Save the currently displayed entries to folder/oto.ini."""
    folder = Path(folder)
    lines = [entry.to_line() for entry in entries]
    (folder / OTO_FILE_NAME).write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
