"""Parser für Mannschaften + Aufstellung (m.html)."""
from __future__ import annotations

from bs4 import BeautifulSoup

from rinkmaster.model import Player, Team

ROLE_MAP = {
    "Nr. 1": "Lead",
    "Nr. 2": "Second",
    "Nr. 3": "Third",
    "Nr. 4": "Skip",
    "Alt.": "Ersatz",
}


def _club_from_name(name: str) -> str | None:
    return name.split(" / ")[0].strip() if " / " in name else None


def parse_teams(m_html: str) -> list[Team]:
    soup = BeautifulSoup(m_html, "html.parser")
    teams: list[Team] = []
    for anchor in soup.select("a[id^='team']"):
        table = anchor.find_next_sibling("div", class_="table")
        if table is None:
            continue
        title = table.select_one(".row.title .cell.team")
        if title is None:
            continue
        name = title.get_text(strip=True)
        players: list[Player] = []
        skip_name: str | None = None
        for mrow in table.select(".row.member"):
            pos_cell = mrow.select_one(".cell.pos")
            player_cell = mrow.select_one(".cell.player")
            if player_cell is None:
                continue
            position = pos_cell.get_text(strip=True) if pos_cell else None
            raw = player_cell.get_text(strip=True)
            is_skip = "(Skip)" in raw
            pname = raw.replace("(Skip)", "").strip()
            if is_skip:
                skip_name = pname
            players.append(Player(
                name=pname,
                position=position,
                role=ROLE_MAP.get(position or ""),
                is_skip=is_skip,
            ))
        teams.append(Team(
            id=anchor.get("id"),
            name=name,
            club=_club_from_name(name),
            skip_name=skip_name,
            players=players,
        ))
    return teams
