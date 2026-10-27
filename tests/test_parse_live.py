from rinkmaster.parse_live import parse_live

_A_EMPTY = open("tests/fixtures/slo_a.html", encoding="utf-8").read()       # echtes a.html ohne Live-Spiele
_A_LIVE = open("tests/fixtures/slo_a_live.html", encoding="utf-8").read()   # .table.current mit einem laufenden Spiel


def test_parse_live_empty_returns_no_games():
    assert parse_live(_A_EMPTY) == []


def test_parse_live_parses_running_game():
    games = parse_live(_A_LIVE)
    assert len(games) == 1
    g = games[0]
    assert g.status == "live"
    assert g.round == 2 and g.date == "26.10.2026" and g.time == "20:15"
    assert g.rink == "Rink C" and g.venue == "Uzwil"
    assert [t.name for t in g.teams] == ["St.Galler Bär / Matt", "Uzwil HeMü / Müller"]
    assert g.hammer_team == "St.Galler Bär / Matt"          # '*' am Namen/T-Spalte
    assert g.teams[0].ends[:5] == [0, 1, 1, 1, None]         # Ends 1–4 gespielt, 5 offen
    assert g.teams[0].total == 3
    assert g.current_end == 5                                # höchstes End mit Wert + 1 = laufendes End
