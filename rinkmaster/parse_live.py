"""Parser für laufende Spiele (``a.html``, Container ``.table.current``).

``a.html`` (nav ``#current`` → «Aktuelle Spiele») nutzt dieselben ``.scoreebe``-
Blöcke wie die Resultate, nur im Container ``.table.current`` und mit noch
unvollständigem Score. Darum wird ``parse_results.parse_scoreebe`` wiederverwendet.

``current_end`` wird aus den Enddaten **abgeleitet** (höchstes End mit einem
Wert) — Rinkmaster liefert für a.html keinen expliziten Marker. Taucht später
ein echter Marker in einem Live-Stand auf, kann ``_current_end`` darauf
umgestellt werden.
"""
from __future__ import annotations

from bs4 import BeautifulSoup

from rinkmaster.model import Game, GameTeam
from rinkmaster.parse_results import parse_scoreebe
from rinkmaster.util import parse_meta


def _current_end(teams: list[GameTeam]) -> int:
    """Höchste End-Nummer (1-basiert), für die irgendein Team einen Wert hat;
    mindestens 1 (End 1 im Gange)."""
    last = 0
    for team in teams:
        for i, value in enumerate(team.ends, start=1):
            if value is not None:
                last = max(last, i)
    return last or 1


def parse_live(a_html: str) -> list[Game]:
    """Liest laufende Spiele aus ``a.html``. Leerer Stand (nur ``.comment``)
    → leere Liste."""
    soup = BeautifulSoup(a_html, "html.parser")
    container = soup.select_one(".table.current")
    games: list[Game] = []
    if container is None:
        return games
    venue = date = time = None
    rnd = None
    for child in container.find_all("div", recursive=False):
        classes = child.get("class", [])
        if "row" in classes and "subtitle" in classes:
            plan = child.select_one(".cell.plan")
            if plan:
                venue, date, time, rnd = parse_meta(plan.get_text(strip=True))
        elif "scoreebe" in classes:
            rink_cell = child.select_one(".row.subtitle2 .cell.teamname")
            rink = rink_cell.get_text(strip=True) if rink_cell else None
            teams, hammer = parse_scoreebe(child)
            games.append(Game(
                round=rnd, date=date, time=time, venue=venue, rink=rink,
                status="live", hammer_team=hammer, teams=teams,
                current_end=_current_end(teams),
            ))
    return games
