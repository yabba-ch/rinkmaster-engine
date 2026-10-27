"""Orchestrierung: ein Runner-Lauf. IO ist injiziert (wp/engine/pusher), darum voll testbar."""
import sys

from runner.selection import events_to_refresh


def run_once(wp, engine, pusher, now):
    """Fuehrt einen Lauf aus und gibt die IDs der erfolgreich aufgefrischten Events zurueck.

    wp.fetch_state() -> (events, interval_min, refresh_requested); wp.clear_refresh().
    engine.build(url, id, name, season, live) -> JSON (dict/str).
    pusher.push(event_id, data, views) -> None.

    Ein Fehler bei einem Event wird isoliert (letzter Stand bleibt stehen), die uebrigen laufen weiter.
    """
    events, interval_min, refresh_requested = wp.fetch_state()
    by_id = {e["id"]: e for e in events}
    due = events_to_refresh(events, interval_min, now, refresh_requested)

    refreshed = []
    for event_id in due:
        e = by_id[event_id]
        try:
            data = engine.build(
                url=e["url"], id=e["id"], name=e.get("name", ""),
                season=e.get("saison", ""), live=bool(e.get("live")),
            )
            pusher.push(e["id"], data, e.get("views"))
            refreshed.append(event_id)
        except Exception as exc:  # Fehler je Event isolieren
            print("[runner] Event %s fehlgeschlagen: %s" % (event_id, exc), file=sys.stderr)

    if refresh_requested:
        wp.clear_refresh()
    return refreshed
