"""Orchestrierung: Rinkmaster-Seiten -> Tournament-JSON. Inkl. CLI."""
from __future__ import annotations

import re

from rinkmaster.model import Game, Tournament, to_json
from rinkmaster.numbering import assign_numbers, game_key
from rinkmaster.parse_live import parse_live
from rinkmaster.parse_plan import parse_plan
from rinkmaster.parse_ranking import parse_ranking
from rinkmaster.parse_results import parse_results
from rinkmaster.util import to_iso_date

STONE_COLORS = ("yellow", "red")   # positional: teams[0]=Gelb, teams[1]=Rot (E1)
_STATUS_PRECEDENCE = {"next": 1, "live": 2, "final": 3}   # final > live > next
from rinkmaster.parse_teams import parse_teams


def _parse_last_update(index_html: str) -> str | None:
    m = re.search(r"Spielstand vom:\s*([\d.]+\s*/\s*[\d:]+)", index_html)
    return m.group(1).strip() if m else None


def _normalize_games(games: list[Game]) -> list[Game]:
    """Setzt site-neutrale Ableitungen: Steinfarbe positional (E1) und
    ISO-Datum (E2). Vorhandene Steinfarben werden nicht überschrieben."""
    for game in games:
        game.date_iso = to_iso_date(game.date)
        for i, team in enumerate(game.teams):
            if i < len(STONE_COLORS) and team.stone_color is None:
                team.stone_color = STONE_COLORS[i]
    return games


def _dedupe(games: list[Game]) -> list[Game]:
    """Ein Spiel kann im Plan (next), in a.html (live) und in den Resultaten
    (final) auftauchen. Je ``game_key`` bleibt der Eintrag mit der höchsten
    Präzedenz (final > live > next)."""
    best: dict[str, Game] = {}
    for game in games:
        key = game_key(game)
        current = best.get(key)
        if current is None or _STATUS_PRECEDENCE[game.status] > _STATUS_PRECEDENCE[current.status]:
            best[key] = game
    return list(best.values())


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

    raw_games: list[Game] = []
    last_update = None
    if index_html:
        raw_games += parse_results(index_html) + parse_plan(index_html)
        last_update = _parse_last_update(index_html)

    current_page = discovery.get("current_page")
    if current_page and pages.get(current_page):
        raw_games += parse_live(pages[current_page])

    games = _normalize_games(assign_numbers(_dedupe(raw_games))) if raw_games else []

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
