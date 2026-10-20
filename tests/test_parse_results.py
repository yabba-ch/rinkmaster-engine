from rinkmaster.parse_results import parse_results

_HTML = open("tests/fixtures/slo_index.html", encoding="utf-8").read()


def test_parse_results_linescore_and_hammer():
    games = parse_results(_HTML)
    meuli = [g for g in games if any("Meuli" in t.name for t in g.teams)][0]
    assert meuli.round == 1 and meuli.venue == "St.Gallen" and meuli.rink == "Rink B"
    top = meuli.teams[0]
    assert top.name == "Herisau-Waldstatt / Meuli" and top.total == 14
    assert top.ends[:4] == [4, 2, 3, 1] and top.ends[4] is None   # blank end -> None
    assert meuli.hammer_team == "Herisau-Waldstatt / Meuli"       # from '*'
    assert meuli.status == "final"


def test_total_ignores_X_and_blank():
    games = parse_results(_HTML)
    matt = [g for g in games if any(t.name.startswith("St.Galler Bär") for t in g.teams)][0]
    top = [t for t in matt.teams if t.name.startswith("St.Galler Bär")][0]
    assert top.total == sum(e for e in top.ends if e is not None)  # X-Ende nicht gezählt
