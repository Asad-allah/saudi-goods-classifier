from __future__ import annotations

import unicodedata


def detect_language(text: str) -> str:
    arabic = 0
    latin = 0
    other_letters = 0

    for char in text or "":
        codepoint = ord(char)
        category = unicodedata.category(char)
        if 0x0600 <= codepoint <= 0x06FF:
            arabic += 1
        elif "A" <= char <= "Z" or "a" <= char <= "z":
            latin += 1
        elif category.startswith("L"):
            other_letters += 1

    if arabic and latin:
        return "MIXED"
    if arabic:
        return "AR"
    if latin and not other_letters:
        return "EN"
    return "OTHER"
