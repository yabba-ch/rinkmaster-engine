"""Kleine Parser-Helfer."""
from __future__ import annotations


def int_or_none(text: str | None) -> int | None:
    """Wandelt reinen Zifferntext in int; alles andere (leer, '–', 'X') -> None."""
    s = (text or "").strip()
    if s.lstrip("-").isdigit():
        return int(s)
    return None
