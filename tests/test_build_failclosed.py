"""Fail-closed: Die Engine darf bei fehlgeschlagenem/blockiertem Fetch KEIN
leeres JSON schreiben, sondern muss mit Exit != 0 abbrechen. Sonst pusht der
Runner leere Daten ueber den guten Stand (Clobber)."""
import pytest

from rinkmaster.build import _cli, is_degenerate
from rinkmaster.model import Team, Tournament


def test_is_degenerate_true_for_empty_tournament():
    assert is_degenerate(Tournament(id="slo", name="SLO")) is True


def test_is_degenerate_false_when_teams_present():
    t = Tournament(id="slo", name="SLO", teams=[Team(id="team1", name="T1")])
    assert is_degenerate(t) is False


def test_cli_exits_nonzero_and_writes_nothing_when_fetch_blocked(tmp_path, monkeypatch):
    """nav.html nicht ladbar (IP-Block/Timeout) -> harter Abbruch, keine Ausgabe."""
    out = tmp_path / "data.json"
    monkeypatch.setattr("rinkmaster.fetch.http_get", lambda url, timeout=15: None)
    with pytest.raises(SystemExit) as ex:
        _cli(["--base-url", "https://blocked.invalid/", "--id", "slo",
              "--name", "SLO", "--season", "2026/27", "--out", str(out)])
    assert ex.value.code not in (0, None)
    assert not out.exists()


def test_cli_exits_nonzero_on_degenerate_result(tmp_path, monkeypatch):
    """nav laedt, aber alle Seiten leer (0 Teams/Spiele/Ranglisten) -> Abbruch."""
    out = tmp_path / "data.json"
    monkeypatch.setattr("rinkmaster.fetch.http_get", lambda url, timeout=15: "<html></html>")
    monkeypatch.setattr("rinkmaster.fetch.load_pages", lambda base, getter=None: {})
    with pytest.raises(SystemExit) as ex:
        _cli(["--base-url", "https://x/", "--id", "slo", "--name", "SLO", "--out", str(out)])
    assert ex.value.code not in (0, None)
    assert not out.exists()
