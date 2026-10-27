"""Parser für laufende Spiele (``a.html``, Container ``.table.current``).

``a.html`` (nav ``#current`` → «Aktuelle Spiele») verwendet ``.result``-Blöcke
(nicht ``.scoreebe`` wie die Resultate) mit identischer innerer Struktur.
Darum wird ``parse_results.parse_scoreebe`` wiederverwendet.

``current_end`` wird abgeleitet: höchstes End mit einem Wert + 1 = das derzeit
gespielte End. Rinkmaster liefert keinen expliziten Marker. Mindestens 1,
maximal 9 (ZE).
"""
from __future__ import annotations

from bs4 import BeautifulSoup

from rinkmaster.model import Game, GameTeam
from rinkmaster.parse_results import parse_scoreebe
from rinkmaster.util import parse_meta


def _current_end(teams: list[GameTeam]) -> int:
    """Laufendes End (1-basiert): höchste End-Nummer mit einem Wert + 1.
    Mindestens 1 (kein End gespielt), maximal 9 (Zusatzend)."""
    last = 0
    for team in teams:
        for i, value in enumerate(team.ends, start=1):
            if value is not None:
                last = max(last, i)
    if last == 0:
        return 1
    return min(last + 1, 9)


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
            # a.html uses .cell.title; older/offline fixtures may use .cell.plan
            plan = child.select_one(".cell.plan, .cell.title")
            if plan:
                venue, date, time, rnd = parse_meta(plan.get_text(strip=True))
        elif "result" in classes:
            # a.html uses .result; strip " - Spiel läuft" suffix Rinkmaster appends
            rink_cell = child.select_one(".row.subtitle2 .cell.teamname")
            rink_text = rink_cell.get_text(strip=True) if rink_cell else None
            rink = rink_text.split(" - ")[0].strip() if rink_text else None
            teams, hammer = parse_scoreebe(child)
            games.append(Game(
                round=rnd, date=date, time=time, venue=venue, rink=rink,
                status="live", hammer_team=hammer, teams=teams,
                current_end=_current_end(teams),
            ))
    return games
