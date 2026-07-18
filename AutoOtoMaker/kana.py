"""Utilities for converting recognized Japanese text into hiragana readings."""

from __future__ import annotations

import re
import unicodedata

try:
    from pykakasi import kakasi
except ImportError:  # pragma: no cover - optional dependency fallback
    kakasi = None

_SMALL_KANA = str.maketrans({
    "ァ": "ぁ", "ィ": "ぃ", "ゥ": "ぅ", "ェ": "ぇ", "ォ": "ぉ",
    "ャ": "ゃ", "ュ": "ゅ", "ョ": "ょ", "ッ": "っ", "ヮ": "ゎ",
})
_KATAKANA_START = ord("ァ")
_KATAKANA_END = ord("ヶ")
_HIRAGANA_OFFSET = ord("ぁ") - ord("ァ")


def katakana_to_hiragana(text: str) -> str:
    """Convert katakana characters in *text* to hiragana."""
    chars: list[str] = []
    for char in text.translate(_SMALL_KANA):
        code = ord(char)
        if _KATAKANA_START <= code <= _KATAKANA_END:
            chars.append(chr(code + _HIRAGANA_OFFSET))
        else:
            chars.append(char)
    return "".join(chars)


def normalize_reading(text: str) -> str:
    """Normalize a reading field to hiragana-only phonetic text where possible."""
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"[\s、。,.!?！？・…\-—―~〜]+", "", text)
    return katakana_to_hiragana(text).lower()


def to_hiragana(text: str) -> str:
    """Convert Japanese text to a hiragana reading.

    pykakasi is used when available so kanji can be converted. If it is not
    installed, the function still normalizes kana text and leaves kanji intact.
    """
    if kakasi is None:
        return normalize_reading(text)

    converter = kakasi()
    result = converter.convert(text)
    reading = "".join(item.get("hira") or item.get("kana") or item.get("orig", "") for item in result)
    return normalize_reading(reading)
