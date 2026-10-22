"""Kleine Parser-Helfer."""
from __future__ import annotations

import re
from datetime import datetime


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


def to_iso_datetime(raw: str | None) -> str | None:
    """'19.10.2026 / 22:22:47' -> '2026-10-19T22:22:47' (E4).

    Naive lokale Zeit ohne Offset (Site und Daten sind beide Schweizer Zeit) —
    bewusst ohne Zeitzonen-Abhängigkeit. None/unparsbar -> None.
    """
    if not raw or "/" not in raw:
        return None
    date_part, _, time_part = raw.partition("/")
    iso_date = to_iso_date(date_part.strip())
    if iso_date is None:
        return None
    t = time_part.strip()
    for fmt in ("%H:%M:%S", "%H:%M"):
        try:
            parsed = datetime.strptime(t, fmt)
        except ValueError:
            continue
        return f"{iso_date}T{parsed.strftime('%H:%M:%S')}"
    return None


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
