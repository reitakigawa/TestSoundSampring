"""Mora segmentation for Japanese hiragana readings."""

from __future__ import annotations

SMALL_ATTACHING = set("ゃゅょぁぃぅぇぉゎ")
MORAIC_SPECIALS = set("っんー")
VOWELS = set("あいうえお")


def split_mora(reading: str) -> list[str]:
    """Split a hiragana reading into mora-like units."""
    morae: list[str] = []
    for char in reading:
        if not char:
            continue
        if char in SMALL_ATTACHING and morae:
            morae[-1] += char
        elif char.strip():
            morae.append(char)
    return morae


def expected_morae(reading: str) -> set[str]:
    """Return unique morae expected from the supplied reading."""
    return set(split_mora(reading))
