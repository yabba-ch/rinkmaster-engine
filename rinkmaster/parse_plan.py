"""Parser für die nächsten Spiele (``#plan`` auf index.html)."""
from __future__ import annotations

from bs4 import BeautifulSoup

from rinkmaster.model import Game, GameTeam
from rinkmaster.util import parse_meta


def parse_plan(index_html: str) -> list[Game]:
    soup = BeautifulSoup(index_html, "html.parser")
    container = soup.select_one(".table.plan")
    games: list[Game] = []
    if container is None:
        return games
    venue = date = time = None
    rnd = None
    for row in container.find_all("div", class_="row", recursive=False):
        classes = row.get("class", [])
        if "subtitle" in classes:
            title = row.select_one(".cell.title")
            if title:
                venue, date, time, rnd = parse_meta(title.get_text(strip=True))
        elif "pairing" in classes:
            rink_cell = row.select_one(".cell.rink")
            rink = rink_cell.get_text(strip=True) if rink_cell else None
            teams = [GameTeam(name=c.get_text(strip=True))
                     for c in row.select(".cell.team")]
            games.append(Game(
                round=rnd, date=date, time=time, venue=venue, rink=rink,
                status="next", hammer_team=None, teams=teams,
            ))
    return games
