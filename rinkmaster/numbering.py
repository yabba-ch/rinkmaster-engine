"""Schema A: global fortlaufende, stabile Spielnummern.

Chronologisch nach Datum -> Zeit -> Rink nummeriert. Der ``game_key`` ist aus
stabilen Spiel-Attributen abgeleitet (teamreihenfolge-unabhängig), damit ein
Spiel seine Nummer behält, wenn es von "nächstes Spiel" zu "Resultat" wandert.
"""
from __future__ import annotations

from rinkmaster.model import Game


def _date_iso(date: str | None) -> str:
    """'19.10.2026' -> '2026-10-19'; leeres/unbekanntes Datum ans Ende."""
    if not date:
        return "9999-99-99"
    try:
        dd, mm, yyyy = date.split(".")
        return f"{yyyy}-{mm}-{dd}"
    except ValueError:
        return "9999-99-99"


def _time_key(time: str | None) -> tuple[int, int]:
    if not time:
        return (99, 99)
    try:
        h, m = time.split(":")
        return (int(h), int(m))
    except ValueError:
        return (99, 99)


def _sort_key(game: Game) -> tuple:
    return (_date_iso(game.date), _time_key(game.time), game.rink or "")


def game_key(game: Game) -> str:
    """Stabiler Schlüssel: round|date|time|rink|sortierte Teamnamen."""
    names = "|".join(sorted(t.name for t in game.teams))
    return f"{game.round}|{game.date}|{game.time}|{game.rink}|{names}"


def assign_numbers(games: list[Game]) -> list[Game]:
    """Sortiert chronologisch und setzt ``number`` = 1..N (in place)."""
    ordered = sorted(games, key=_sort_key)
    for i, game in enumerate(ordered, start=1):
        game.number = i
    return ordered
