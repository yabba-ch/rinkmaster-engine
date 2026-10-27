"""Reine Auswahl-Logik: welche Events ein Runner-Lauf auffrischt. Kein IO, voll testbar."""
from datetime import timedelta


def events_to_refresh(events, interval_min, now, refresh_requested):
    """IDs der aktiven, faelligen Events.

    events: Liste von Mappings mit 'id', 'aktiv' (bool), 'last_updated' (datetime|None).
    interval_min: globales Aktualisierungs-Intervall in Minuten.
    now: aktueller Zeitpunkt (datetime, gleiche tz-Konvention wie last_updated).
    refresh_requested: wenn True, sind alle aktiven Events faellig (unabhaengig vom Intervall).

    Faellig = aktiv UND (refresh_requested ODER noch nie geparst ODER
    seit last_updated >= interval_min Minuten vergangen).
    """
    due = []
    for e in events:
        if not e.get("aktiv"):
            continue
        if refresh_requested:
            due.append(e["id"])
            continue
        last_updated = e.get("last_updated")
        if last_updated is None or (now - last_updated) >= timedelta(minutes=interval_min):
            due.append(e["id"])
    return due
