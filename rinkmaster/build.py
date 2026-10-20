"""Orchestrierung: Rinkmaster-Seiten -> Tournament-JSON. Inkl. CLI."""
from __future__ import annotations

import re

from rinkmaster.model import Tournament, to_json
from rinkmaster.numbering import assign_numbers
from rinkmaster.parse_plan import parse_plan
from rinkmaster.parse_ranking import parse_ranking
from rinkmaster.parse_results import parse_results
from rinkmaster.parse_teams import parse_teams


def _parse_last_update(index_html: str) -> str | None:
    m = re.search(r"Spielstand vom:\s*([\d.]+\s*/\s*[\d:]+)", index_html)
    return m.group(1).strip() if m else None


def build_tournament(pages: dict[str, str | None], discovery: dict, meta: dict) -> Tournament:
    """Fügt Ranglisten, Teams und Spiele (nummeriert) zu einem Tournament zusammen."""
    index_html = pages.get("index.html")

    rankings = []
    for r in discovery.get("rankings", []):
        page_html = pages.get(r["page"])
        if page_html:
            rankings.append(parse_ranking(page_html, ranking_id=r["id"], label=r["label"]))

    teams = []
    teams_page = discovery.get("teams_page")
    if teams_page and pages.get(teams_page):
        teams = parse_teams(pages[teams_page])

    # Rang/Punkte/Steine aus der Hauptrangliste in die Teams übernehmen
    # (per team_id); so trägt jedes Team seine Werte, ohne die Normalisierung
    # in rankings[] zu verlieren.
    if rankings and teams:
        by_id = {row.team_id: row for row in rankings[0].rows if row.team_id}
        for team in teams:
            row = by_id.get(team.id)
            if row:
                team.rank = row.rank
                team.points = row.points
                team.ends = row.ends
                team.stones = row.stones

    games = []
    last_update = None
    if index_html:
        games = assign_numbers(parse_results(index_html) + parse_plan(index_html))
        last_update = _parse_last_update(index_html)

    return Tournament(
        id=meta["id"],
        name=meta["name"],
        season=meta.get("season"),
        last_update=last_update,
        live=meta.get("live", False),
        teams=teams,
        rankings=rankings,
        games=games,
    )


def _cli(argv: list[str] | None = None) -> None:
    import argparse

    from rinkmaster.fetch import discover, http_get, load_pages

    parser = argparse.ArgumentParser(description="Rinkmaster -> Tournament JSON")
    parser.add_argument("--base-url", required=True, help="z.B. https://host/pfad/")
    parser.add_argument("--id", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--season")
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--out", help="Zieldatei (sonst stdout)")
    args = parser.parse_args(argv)

    base = args.base_url if args.base_url.endswith("/") else args.base_url + "/"
    nav = http_get(base + "nav.html")
    discovery = discover(nav) if nav else {"rankings": [], "teams_page": None, "current_page": None}
    pages = load_pages(base)
    tournament = build_tournament(pages, discovery, meta={
        "id": args.id, "name": args.name, "season": args.season, "live": args.live,
    })
    output = to_json(tournament)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(output)
    else:
        print(output)


if __name__ == "__main__":
    _cli()
