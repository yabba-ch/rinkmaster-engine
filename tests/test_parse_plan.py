from rinkmaster.parse_plan import parse_plan

_HTML = open("tests/fixtures/slo_index.html", encoding="utf-8").read()


def test_parse_plan_pairings():
    games = parse_plan(_HTML)
    g = games[0]
    assert g.round == 2 and g.venue == "Uzwil" and g.rink == "Rink D"
    assert [t.name for t in g.teams] == ["CC Uzwil / Bauer", "CC Thurgau / Höchner"]
    assert g.status == "next" and g.teams[0].total is None and g.teams[0].ends == []
    assert g.hammer_team is None
    assert all(len(x.teams) == 2 for x in games)
