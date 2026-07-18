"""Alias generation for Japanese continuous-sound UTAU oto entries."""

from __future__ import annotations

VOWELS = {
    "あ": "a", "い": "i", "う": "u", "え": "e", "お": "o",
    "ぁ": "a", "ぃ": "i", "ぅ": "u", "ぇ": "e", "ぉ": "o",
    "か": "a", "が": "a", "さ": "a", "ざ": "a", "た": "a", "だ": "a", "な": "a", "は": "a", "ば": "a", "ぱ": "a", "ま": "a", "や": "a", "ゃ": "a", "ら": "a", "わ": "a",
    "き": "i", "ぎ": "i", "し": "i", "じ": "i", "ち": "i", "ぢ": "i", "に": "i", "ひ": "i", "び": "i", "ぴ": "i", "み": "i", "り": "i",
    "く": "u", "ぐ": "u", "す": "u", "ず": "u", "つ": "u", "づ": "u", "ぬ": "u", "ふ": "u", "ぶ": "u", "ぷ": "u", "む": "u", "ゆ": "u", "ゅ": "u", "る": "u",
    "け": "e", "げ": "e", "せ": "e", "ぜ": "e", "て": "e", "で": "e", "ね": "e", "へ": "e", "べ": "e", "ぺ": "e", "め": "e", "れ": "e",
    "こ": "o", "ご": "o", "そ": "o", "ぞ": "o", "と": "o", "ど": "o", "の": "o", "ほ": "o", "ぼ": "o", "ぽ": "o", "も": "o", "よ": "o", "ょ": "o", "ろ": "o", "を": "o", "ん": "n", "っ": "cl", "ー": "-",
}


def mora_vowel(mora: str) -> str:
    """Return the vowel/transition symbol for a mora."""
    for char in reversed(mora):
        if char in VOWELS:
            return VOWELS[char]
    return mora[-1:] or "-"


def make_alias(previous_mora: str | None, current_mora: str, start_of_phrase: bool = False) -> str:
    """Create a CVVC/VCV-style continuous alias such as ``a か`` or ``- あ``."""
    prefix = "-" if start_of_phrase or not previous_mora else mora_vowel(previous_mora)
    return f"{prefix} {current_mora}"
