"""parse_scoreebe muss mit variabler Spaltenzahl umgehen: Resultate-Tabellen mit
Zusatzend (slo/osl: 12 Zellen) UND ohne Zusatzend-Spalte (hma: 11 Zellen).
Ohne Fix verwirft der 12-Zellen-Guard die hma-Zeilen -> teams leer."""
from bs4 import BeautifulSoup

from rinkmaster.parse_results import parse_scoreebe


def _cell(text):
    return '<div class="cell">' + text + "</div>"


def _row(cells, cls="row scoreplayed"):
    return '<div class="' + cls + '">' + "".join(_cell(c) for c in cells) + "</div>"


def _scoreebe(*rows):
    return BeautifulSoup('<div class="scoreebe">' + "".join(rows) + "</div>", "html.parser").select_one(".scoreebe")


# hma: 11 Zellen = Name, H, Ends 1-8, Total (KEINE Zusatzend-Spalte)
HMA = _scoreebe(
    _row(["Rink A", "T", "1", "2", "3", "4", "5", "6", "7", "8", "Total"], cls="row subtitle2"),
    _row(["Attinger / Werner Attinger", "", "1", "2", "", "", "2", "", "1", "", "6"]),
    _row(["d'Appenzeller / Daniel Meuli*", "*", "", "", "2", "2", "", "1", "", "3", "8"]),
)

# slo/osl: 12 Zellen = Name, H, Ends 1-8, ZE, Total
TWELVE = _scoreebe(
    _row(["A", "", "1", "2", "3", "4", "5", "6", "7", "8", "2", "38"]),
    _row(["B*", "*", "0", "0", "0", "0", "0", "0", "0", "0", "1", "1"]),
)


def test_eleven_cells_no_ze_parses_both_teams():
    teams, hammer = parse_scoreebe(HMA)
    assert len(teams) == 2
    assert teams[0].name == "Attinger / Werner Attinger"
    assert teams[0].total == 6
    assert teams[0].ends[:8] == [1, 2, None, None, 2, None, 1, None]
    assert len(teams[0].ends) == 9 and teams[0].ends[8] is None   # ZE-Slot leer
    assert teams[1].total == 8
    assert hammer == "d'Appenzeller / Daniel Meuli"               # aus '*'


def test_twelve_cells_with_ze_still_works():
    teams, hammer = parse_scoreebe(TWELVE)
    assert len(teams) == 2
    assert len(teams[0].ends) == 9 and teams[0].ends[8] == 2      # ZE erhalten
    assert teams[0].total == 38
    assert hammer == "B"
