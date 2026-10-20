from rinkmaster.model import Tournament, Team, Player, to_json


def test_to_json_preserves_umlauts_and_shape():
    t = Tournament(
        id="slo", name="SLO", season="2026/27", last_update=None, live=False,
        teams=[Team(id="team1", name="CC Thurgau / Höchner", club="CC Thurgau",
                    skip_name="Michael Höchner",
                    players=[Player("Michael Höchner", "Skip", "Skip", True)],
                    rank=2, points=3, ends=5, stones=15)],
        rankings=[], games=[])
    s = to_json(t)
    assert "Höchner" in s            # umlauts not escaped to ö
    import json
    d = json.loads(s)
    assert d["teams"][0]["players"][0]["is_skip"] is True
    assert d["teams"][0]["rank"] == 2
