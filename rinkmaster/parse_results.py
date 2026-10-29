"""Parser für gespielte Spiele (``#results`` auf index.html)."""
from __future__ import annotations

from bs4 import BeautifulSoup
from bs4.element import Tag

from rinkmaster.model import Game, GameTeam
from rinkmaster.util import int_or_none, parse_meta


def parse_scoreebe(scoreebe: Tag) -> tuple[list[GameTeam], str | None]:
    """Liest einen ``.scoreebe``-Block: beide Teams mit End-für-End-Score und
    Total, plus das Team mit Hammer (letzter Stein im 1. End, ``*``).

    End-Liste = Ends 1–8 + Zusatzend (9 Werte); Ziffer -> int, Leer/``X`` -> None.
    Wird vom späteren Live-Parser (a.html) wiederverwendet.
    """
    teams: list[GameTeam] = []
    hammer: str | None = None
    for row in scoreebe.find_all("div", class_="row", recursive=False):
        classes = row.get("class", [])
        if "subtitle2" in classes:
            continue
        cells = row.find_all("div", class_="cell", recursive=False)
        if len(cells) < 4:      # mind. Name + Hammer + 1 End + Total
            continue
        name_raw = cells[0].get_text(strip=True)
        has_hammer = name_raw.endswith("*") or "*" in cells[1].get_text(strip=True)
        name = name_raw.rstrip("*").strip()
        # Ends = alle Zellen zwischen Hammer-Spalte und Total. Die Spaltenzahl
        # variiert je Turnier: mit Zusatzend (12 Zellen) oder ohne (11 Zellen,
        # z.B. SG Hallen-Meisterschaft). Auf Laenge 9 normalisieren (Ends 1-8 +
        # ZE), damit der JSON-Vertrag (immer 9) und der Renderer stimmen.
        ends = [int_or_none(c.get_text()) for c in cells[2:-1]]
        ends = (ends + [None] * 9)[:9]
        total = int_or_none(cells[-1].get_text(strip=True))
        teams.append(GameTeam(name=name, total=total, ends=ends))
        if has_hammer:
            hammer = name
    return teams, hammer


def parse_results(index_html: str) -> list[Game]:
    soup = BeautifulSoup(index_html, "html.parser")
    container = soup.select_one(".table.results")
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
                status="final", hammer_team=hammer, teams=teams,
            ))
    return games
