from rinkmaster.fetch import discover, load_pages


def test_discover_reads_rankings_and_optional_pages():
    nav = open("tests/fixtures/slo_nav.html", encoding="utf-8").read()
    d = discover(nav)
    assert d["rankings"][0] == {"id": "ranking0", "label": "Gesamtrangliste", "page": "index.html"}
    assert d["teams_page"] == "m.html"
    assert d["current_page"] == "a.html"


def test_discover_handles_missing_teams_and_current():
    nav = open("tests/fixtures/cundj_nav.html", encoding="utf-8").read()
    d = discover(nav)
    assert d["teams_page"] is None and d["current_page"] is None
    assert [r["id"] for r in d["rankings"]] == ["ranking0", "ranking1", "ranking2", "ranking3"]


def test_load_pages_tolerates_404():
    nav = open("tests/fixtures/tgm_nav.html", encoding="utf-8").read()
    fake = {"nav.html": nav, "index.html": "<html>ok</html>", "ta.html": None,
            "m.html": "<m>", "a.html": "<a>"}
    pages = load_pages("http://x/", getter=lambda u: fake.get(u.rsplit("/", 1)[-1]))
    assert pages["ta.html"] is None
    assert pages["index.html"] == "<html>ok</html>"
