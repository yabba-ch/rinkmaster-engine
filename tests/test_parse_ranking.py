from rinkmaster.parse_ranking import parse_ranking


def test_parse_ranking_rows():
    html = open("tests/fixtures/slo_index.html", encoding="utf-8").read()
    r = parse_ranking(html)
    assert len(r.rows) == 10
    first = r.rows[0]
    assert first.rank == 1
    assert first.team_name == "Herisau-Waldstatt / Meuli"
    assert (first.points, first.ends, first.stones, first.played) == (3, 6, 14, 1)
    assert r.rows[1].team_name == "CC Thurgau / Höchner"   # umlaut intact
    assert first.team_id == "team3"
    # team with empty rank cell keeps None, not a crash
    junker = [x for x in r.rows if x.team_name == "ITConcepts / Junker"][0]
    assert junker.rank is None
