from rinkmaster.util import to_iso_date, to_iso_datetime


def test_to_iso_date_valid():
    assert to_iso_date("19.10.2026") == "2026-10-19"


def test_to_iso_date_none_and_unparsable():
    assert to_iso_date(None) is None
    assert to_iso_date("") is None
    assert to_iso_date("19.10.") is None      # kein Jahr
    assert to_iso_date("Mo. 19.10.2026") is None  # Zusatztext


def test_to_iso_datetime_valid():
    assert to_iso_datetime("19.10.2026 / 22:22:47") == "2026-10-19T22:22:47"
    assert to_iso_datetime("19.10.2026 / 20:15") == "2026-10-19T20:15:00"   # Sekunden ergänzt


def test_to_iso_datetime_none_and_unparsable():
    assert to_iso_datetime(None) is None
    assert to_iso_datetime("") is None
    assert to_iso_datetime("19.10.2026") is None      # keine Zeit
    assert to_iso_datetime("19.10.2026 / 25:99") is None  # ungültige Zeit
