import json

from rinkmaster.build import build_tournament
from rinkmaster.fetch import discover
from rinkmaster.model import to_json
from rinkmaster.parse_plan import parse_plan
from rinkmaster.parse_results import parse_results

_IDX = open("tests/fixtures/slo_index.html", encoding="utf-8").read()
_M = open("tests/fixtures/slo_m.html", encoding="utf-8").read()
_NAV = open("tests/fixtures/slo_nav.html", encoding="utf-8").read()
_A_LIVE = open("tests/fixtures/slo_a_live.html", encoding="utf-8").read()


def test_build_from_fixtures_assembles_full_json():
    pages = {"index.html": _IDX, "m.html": _M, "a.html": None}
    disc = discover(_NAV)
    t = build_tournament(pages, disc,
                         meta={"id": "slo", "name": "SLO", "season": "2026/27", "live": False})
    d = json.loads(to_json(t))
    assert d["id"] == "slo"
    assert len(d["teams"]) == 10
    assert d["rankings"][0]["label"] == "Gesamtrangliste"
    expected = len(parse_results(_IDX)) + len(parse_plan(_IDX))
    assert len(d["games"]) == expected
    nums = sorted(g["number"] for g in d["games"])
    assert nums == list(range(1, expected + 1))           # fortlaufend + eindeutig
    assert any(g["status"] == "final" for g in d["games"])
    assert any(g["status"] == "next" for g in d["games"])
    assert d["last_update"] == "19.10.2026 / 22:22:47"
    assert d["last_update_iso"] == "2026-10-19T22:22:47"      # E4


def test_teams_enriched_from_primary_ranking():
    pages = {"index.html": _IDX, "m.html": _M, "a.html": None}
    disc = discover(_NAV)
    t = build_tournament(pages, disc, meta={"id": "slo", "name": "SLO", "live": False})
    hoe = [x for x in t.teams if x.id == "team9"][0]   # CC Thurgau / Höchner, Rang 2
    assert (hoe.rank, hoe.points, hoe.ends, hoe.stones) == (2, 3, 5, 15)


def test_games_have_positional_stone_color_and_iso_date():
    pages = {"index.html": _IDX, "m.html": _M, "a.html": None}
    disc = discover(_NAV)
    t = build_tournament(pages, disc, meta={"id": "slo", "name": "SLO", "live": False})
    d = json.loads(to_json(t))
    g = d["games"][0]
    assert len(g["teams"]) == 2
    assert g["teams"][0]["stone_color"] == "yellow"   # E1 positional
    assert g["teams"][1]["stone_color"] == "red"
    assert g["date_iso"] and len(g["date_iso"]) == 10 and g["date_iso"][4] == "-"  # E2 yyyy-mm-dd


def test_schema_version_is_first_key():
    pages = {"index.html": _IDX, "m.html": _M, "a.html": None}
    disc = discover(_NAV)
    t = build_tournament(pages, disc, meta={"id": "slo", "name": "SLO", "live": False})
    d = json.loads(to_json(t))
    assert d["schema"] == 1                      # E5
    assert list(d.keys())[0] == "schema"


def test_live_game_from_current_page_is_merged():
    pages = {"index.html": _IDX, "m.html": _M, "a.html": _A_LIVE}
    disc = discover(_NAV)                         # nav: current_page = a.html
    t = build_tournament(pages, disc, meta={"id": "slo", "name": "SLO", "live": True})
    d = json.loads(to_json(t))
    live = [g for g in d["games"] if g["status"] == "live"]
    assert len(live) == 1
    assert live[0]["current_end"] == 4            # E3
    assert live[0]["teams"][0]["stone_color"] == "yellow"   # Normalisierung greift auch live
    assert live[0]["date_iso"] == "2026-10-26"
