"""Fast, conservative token normalization shared by catalog and user input."""

from __future__ import annotations

import re

from app.nlp.normalizer import normalize_text

_TOKEN_PATTERN = re.compile(r"[a-z]+|[\u0621-\u064a]+")


def normalized_tokens(text: str) -> tuple[str, ...]:
    """Return Arabic/Latin tokens after the service's shared normalization."""
    return tuple(_TOKEN_PATTERN.findall(normalize_text(text)))


def token_variants(token: str) -> frozenset[str]:
    """Return safe lexical variants, never an unconstrained Arabic stem.

    The variants cover deterministic spelling and light inflection differences
    that matter for goods descriptions. They are generated for both catalog and
    request tokens, so a match never depends on a one-sided manual alias.
    """
    variants = {token}
    if _is_arabic_token(token):
        if token.startswith("ال") and len(token) >= 5:
            variants.add(token[2:])
        if token.endswith("ه") and len(token) >= 4:
            variants.add(f"{token[:-1]}ا")
            if len(token) >= 5:
                variants.add(token[:-1])
        elif token.endswith("ا") and len(token) >= 4:
            variants.add(f"{token[:-1]}ه")
        if token.endswith("ات") and len(token) >= 5:
            variants.add(token[:-2])
        if token.endswith(("ون", "ين")) and len(token) >= 6:
            variants.add(token[:-2])
    else:
        if token.endswith("ies") and len(token) >= 5:
            variants.add(f"{token[:-3]}y")
        elif token.endswith("es") and len(token) >= 5:
            variants.add(token[:-2])
        elif token.endswith("s") and len(token) >= 4:
            variants.add(token[:-1])
    return frozenset(variant for variant in variants if len(variant) >= 3)


def text_token_variants(text: str) -> frozenset[str]:
    return frozenset(
        variant for token in normalized_tokens(text) for variant in token_variants(token)
    )


def _is_arabic_token(token: str) -> bool:
    return bool(token) and all("\u0621" <= char <= "\u064a" for char in token)
