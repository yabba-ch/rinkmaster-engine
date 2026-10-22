from rinkmaster.util import to_iso_date


def test_to_iso_date_valid():
    assert to_iso_date("19.10.2026") == "2026-10-19"


def test_to_iso_date_none_and_unparsable():
    assert to_iso_date(None) is None
    assert to_iso_date("") is None
    assert to_iso_date("19.10.") is None      # kein Jahr
    assert to_iso_date("Mo. 19.10.2026") is None  # Zusatztext
