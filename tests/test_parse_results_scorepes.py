"""Weinfelden-Quellen (TGM, cc-tg) liefern fertige Spiele im ``.scorepes``-
Format: P-E-S als ein String (``"2-5-8"`` = Punkte-Ends-Steine), ohne
End-fuer-End-Details. parse_results muss diese als finale Spiele mit
points/ends_won/total (= Steine) liefern, damit der Resultate-Tab sie zeigt.
"""
from rinkmaster.parse_results import parse_results

_TGM = open("tests/fixtures/tgm_index.html", encoding="utf-8").read()


def test_parse_results_scorepes_pes():
    games = parse_results(_TGM)
    junker = [g for g in games
              if g.status == "final" and any("Junker" in t.name for t in g.teams)]
    assert junker, "scorepes-Resultat (Runde 1, Junker/Signer) wurde nicht geparst"
    g = junker[0]
    assert g.round == 1 and g.rink == "Rink A"
    j = [t for t in g.teams if "Junker" in t.name][0]
    s = [t for t in g.teams if "Signer" in t.name][0]
    assert (j.points, j.ends_won, j.total) == (2, 5, 8)   # Punkte-Ends-Steine
    assert (s.points, s.ends_won, s.total) == (0, 3, 4)
    assert j.ends == []        # scorepes hat keine End-fuer-End-Details


def test_parse_results_scorepes_count():
    """Beide gespielten Runde-1-Partien (Rink A und Rink B) werden gelesen."""
    finals = [g for g in parse_results(_TGM) if g.status == "final"]
    assert len(finals) == 2
    rinks = sorted(g.rink for g in finals)
    assert rinks == ["Rink A", "Rink B"]
