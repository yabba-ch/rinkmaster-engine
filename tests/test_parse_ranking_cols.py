"""parse_ranking muss die Spalten ueber die Header-Zeile zuordnen: Ranglisten mit
"Pt. Dir."-Spalte (slo: 8 Spalten) UND ohne (hma/osl: 7 Spalten). Bei festen
Indizes landet "Spiele" sonst in der falschen/leeren Zelle -> played = None."""
from rinkmaster.parse_ranking import parse_ranking


def _cell(text):
    return '<div class="cell">' + text + "</div>"


def _team_cell(team_id, name):
    return ('<div class="cell"><span class="teamname"><a href="m.html#' + team_id + '">'
            + name + "</a></span>Spieler X (Skip)</div>")


def _table(headers, row_cells):
    head = '<div class="row title">' + "".join(_cell(h) for h in headers) + "</div>"
    body = '<div class="row">' + row_cells + "</div>"
    return '<div class="table ranking">' + head + body + "</div>"


# 7 Spalten (hma/osl): KEINE "Pt. Dir."-Spalte -> "Spiele" an Index 5
SEVEN = _table(
    ["Rang", "Mannschaft", "Punkte", "Ends", "Steine", "Spiele", ""],
    _cell("1") + _team_cell("team3", "Eagles / Brunner") + _cell("2") + _cell("5") + _cell("12") + _cell("1") + _cell(""),
)

# 8 Spalten (slo): mit "Pt. Dir." -> "Spiele" an Index 6
EIGHT = _table(
    ["Rang", "Mannschaft", "Punkte", "Ends", "Steine", "Pt. Dir.", "Spiele", ""],
    _cell("1") + _team_cell("team1", "Herisau / Meuli") + _cell("6") + _cell("10") + _cell("21") + _cell("0") + _cell("2") + _cell(""),
)


def test_seven_columns_without_ptdir_reads_played():
    r = parse_ranking(SEVEN)
    assert len(r.rows) == 1
    row = r.rows[0]
    assert (row.points, row.ends, row.stones) == (2, 5, 12)
    assert row.played == 1          # aus "Spiele" (Index 5), nicht aus leerer Zelle 6
    assert row.pt_dir is None       # Spalte existiert in diesem Layout nicht
    assert row.team_name == "Eagles / Brunner" and row.team_id == "team3"


def test_eight_columns_with_ptdir_still_works():
    r = parse_ranking(EIGHT)
    row = r.rows[0]
    assert (row.points, row.ends, row.stones) == (6, 10, 21)
    assert row.pt_dir == 0 and row.played == 2
