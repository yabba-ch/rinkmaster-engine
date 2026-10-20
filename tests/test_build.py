import json

from rinkmaster.build import build_tournament
from rinkmaster.fetch import discover
from rinkmaster.model import to_json
from rinkmaster.parse_plan import parse_plan
from rinkmaster.parse_results import parse_results

_IDX = open("tests/fixtures/slo_index.html", encoding="utf-8").read()
_M = open("tests/fixtures/slo_m.html", encoding="utf-8").read()
_NAV = open("tests/fixtures/slo_nav.html", encoding="utf-8").read()


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


def test_teams_enriched_from_primary_ranking():
    pages = {"index.html": _IDX, "m.html": _M, "a.html": None}
    disc = discover(_NAV)
    t = build_tournament(pages, disc, meta={"id": "slo", "name": "SLO", "live": False})
    hoe = [x for x in t.teams if x.id == "team9"][0]   # CC Thurgau / Höchner, Rang 2
    assert (hoe.rank, hoe.points, hoe.ends, hoe.stones) == (2, 3, 5, 15)
