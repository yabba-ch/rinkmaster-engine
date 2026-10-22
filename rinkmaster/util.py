"""Kleine Parser-Helfer."""
from __future__ import annotations

import re


def int_or_none(text: str | None) -> int | None:
    """Wandelt reinen Zifferntext in int; alles andere (leer, '–', 'X') -> None."""
    s = (text or "").strip()
    if s.lstrip("-").isdigit():
        return int(s)
    return None


def to_iso_date(date: str | None) -> str | None:
    """'19.10.2026' -> '2026-10-19'; None/unparsbar -> None (E2).

    Anders als ``numbering._date_iso`` (das zum Sortieren einen Sentinel
    liefert) gibt diese Funktion bei fehlendem/kaputtem Datum ``None`` zurück.
    """
    if not date:
        return None
    try:
        dd, mm, yyyy = date.split(".")
    except ValueError:
        return None
    if not (dd.isdigit() and mm.isdigit() and yyyy.isdigit()):
        return None
    return f"{yyyy}-{mm}-{dd}"


def parse_meta(text: str) -> tuple[str | None, str | None, str | None, int | None]:
    """Zerlegt eine Rinkmaster-Kopfzeile wie
    ``"St.Gallen, Mo. 19.10.2026, 20:15, , Runde 1"`` in
    ``(venue, date 'dd.mm.yyyy', time 'HH:MM', round)``."""
    parts = [p.strip() for p in text.split(",")]
    venue = parts[0] if parts and parts[0] else None
    date_m = re.search(r"(\d{2}\.\d{2}\.\d{4})", text)
    time_m = re.search(r"(\d{1,2}:\d{2})", text)
    round_m = re.search(r"Runde\s+(\d+)", text)
    return (
        venue,
        date_m.group(1) if date_m else None,
        time_m.group(1) if time_m else None,
        int(round_m.group(1)) if round_m else None,
    )
