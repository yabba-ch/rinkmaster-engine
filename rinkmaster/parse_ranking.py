"""Parser für die Rangliste (``#ranking`` auf index.html)."""
from __future__ import annotations

from bs4 import BeautifulSoup

from rinkmaster.model import Ranking, RankingRow
from rinkmaster.util import int_or_none


def parse_ranking(index_html: str, ranking_id: str = "ranking0",
                  label: str = "Gesamtrangliste") -> Ranking:
    soup = BeautifulSoup(index_html, "html.parser")
    table = soup.select_one(".table.ranking")
    rows: list[RankingRow] = []
    if table is None:
        return Ranking(id=ranking_id, label=label, rows=rows)

    # Spalten ueber die Header-Zeile zuordnen. Die Spaltenzahl variiert je Turnier
    # (z.B. mit/ohne "Pt. Dir."); feste Indizes wuerden "Spiele" sonst verschieben.
    header = table.select_one(".row.title")
    col: dict[str, int] = {}
    if header:
        for i, c in enumerate(header.find_all("div", class_="cell", recursive=False)):
            name = c.get_text(strip=True)
            if name and name not in col:
                col[name] = i

    def val(cells: list, name: str) -> int | None:
        i = col.get(name)
        if i is None or i >= len(cells):
            return None
        return int_or_none(cells[i].get_text(strip=True))

    for row in table.select(".row"):
        classes = row.get("class", [])
        if "title" in classes:
            continue
        cells = row.find_all("div", class_="cell", recursive=False)
        if len(cells) < 3:          # mind. Rang + Team + eine Kennzahl
            continue
        team_cell = cells[1]
        link = team_cell.select_one(".teamname a")
        team_name = link.get_text(strip=True) if link else team_cell.get_text(strip=True)
        href = link.get("href") if link else None
        team_id = href.split("#")[-1] if href and "#" in href else None
        rows.append(RankingRow(
            rank=int_or_none(cells[0].get_text(strip=True)),
            team_id=team_id,
            team_name=team_name,
            points=val(cells, "Punkte"),
            ends=val(cells, "Ends"),
            stones=val(cells, "Steine"),
            pt_dir=val(cells, "Pt. Dir."),
            played=val(cells, "Spiele"),
        ))
    return Ranking(id=ranking_id, label=label, rows=rows)
