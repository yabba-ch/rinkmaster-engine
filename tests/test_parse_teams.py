from rinkmaster.parse_teams import parse_teams

_HTML = open("tests/fixtures/slo_m.html", encoding="utf-8").read()


def test_parse_teams_roster_and_roles():
    teams = parse_teams(_HTML)
    hoe = [t for t in teams if t.id == "team9"][0]
    assert hoe.name == "CC Thurgau / Höchner"
    assert hoe.players[0].name == "Michael Höchner"
    assert hoe.players[0].role == "Skip" and hoe.players[0].is_skip is True
    assert hoe.players[-1].role == "Ersatz"            # Alt.
    assert hoe.skip_name == "Michael Höchner"


def test_skip_flag_from_marker_not_position():
    teams = parse_teams(_HTML)
    bat = [t for t in teams if t.name.endswith("Battilana")][0]
    skips = [p for p in bat.players if p.is_skip]
    assert len(skips) == 1 and skips[0].name == "Paul Battilana"
