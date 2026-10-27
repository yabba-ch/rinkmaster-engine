"""Tests fuer runner.selection.events_to_refresh (reine Auswahl-Logik, kein IO)."""
from datetime import datetime, timedelta

from runner.selection import events_to_refresh

NOW = datetime(2026, 10, 27, 12, 0, 0)


def _ev(event_id, aktiv=True, last_updated=None):
    return {"id": event_id, "aktiv": aktiv, "last_updated": last_updated}


def test_never_parsed_included():
    assert events_to_refresh([_ev("a")], 10, NOW, False) == ["a"]


def test_within_interval_skipped():
    e = _ev("a", last_updated=NOW - timedelta(minutes=3))
    assert events_to_refresh([e], 10, NOW, False) == []


def test_past_interval_included():
    e = _ev("a", last_updated=NOW - timedelta(minutes=11))
    assert events_to_refresh([e], 10, NOW, False) == ["a"]


def test_exactly_interval_included():
    e = _ev("a", last_updated=NOW - timedelta(minutes=10))
    assert events_to_refresh([e], 10, NOW, False) == ["a"]


def test_inactive_never():
    e = _ev("a", aktiv=False, last_updated=None)
    assert events_to_refresh([e], 10, NOW, False) == []
    assert events_to_refresh([e], 10, NOW, True) == []


def test_refresh_forces_all_active():
    e1 = _ev("a", last_updated=NOW - timedelta(minutes=1))  # eigentlich noch nicht faellig
    e2 = _ev("b", aktiv=False)
    assert events_to_refresh([e1, e2], 10, NOW, True) == ["a"]
