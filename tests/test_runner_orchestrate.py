"""Tests fuer runner.orchestrate.run_once mit Fakes (kein echtes IO)."""
from datetime import datetime

from runner.orchestrate import run_once

NOW = datetime(2026, 10, 27, 12, 0, 0)


class FakeWP:
    def __init__(self, events, interval=10, refresh=False):
        self._events, self._interval, self._refresh = events, interval, refresh
        self.cleared = False

    def fetch_state(self):
        return (self._events, self._interval, self._refresh)

    def clear_refresh(self):
        self.cleared = True


class FakeEngine:
    def __init__(self, fail_ids=()):
        self.calls = []
        self.fail_ids = set(fail_ids)

    def build(self, url, id, name, season, live):
        self.calls.append({"id": id, "url": url, "name": name, "season": season, "live": live})
        if id in self.fail_ids:
            raise RuntimeError("engine kaputt")
        return {"games": [{"event": id}]}


class FakePusher:
    def __init__(self):
        self.pushes = []

    def push(self, event_id, data, views):
        self.pushes.append({"id": event_id, "data": data, "views": views})


def _ev(event_id, aktiv=True, last_updated=None, live=False):
    return {
        "id": event_id, "aktiv": aktiv, "last_updated": last_updated, "live": live,
        "views": {"resultate": True}, "url": "http://x/" + event_id + "/",
        "name": event_id.upper(), "saison": "2026/27",
    }


def test_only_due_parsed_and_pushed():
    wp = FakeWP([_ev("a"), _ev("b", aktiv=False)])
    eng, push = FakeEngine(), FakePusher()
    run_once(wp, eng, push, NOW)
    assert [c["id"] for c in eng.calls] == ["a"]
    assert [p["id"] for p in push.pushes] == ["a"]


def test_live_flag_passed():
    wp = FakeWP([_ev("a", live=True)])
    eng, push = FakeEngine(), FakePusher()
    run_once(wp, eng, push, NOW)
    assert eng.calls[0]["live"] is True


def test_views_passed_to_pusher():
    wp = FakeWP([_ev("a")])
    eng, push = FakeEngine(), FakePusher()
    run_once(wp, eng, push, NOW)
    assert push.pushes[0]["views"] == {"resultate": True}


def test_refresh_cleared_after_run():
    wp = FakeWP([_ev("a", last_updated=NOW)], refresh=True)  # eigentlich nicht faellig, refresh erzwingt
    eng, push = FakeEngine(), FakePusher()
    run_once(wp, eng, push, NOW)
    assert wp.cleared is True
    assert [c["id"] for c in eng.calls] == ["a"]


def test_no_clear_when_no_refresh():
    wp = FakeWP([_ev("a")], refresh=False)
    eng, push = FakeEngine(), FakePusher()
    run_once(wp, eng, push, NOW)
    assert wp.cleared is False


def test_engine_error_isolated():
    wp = FakeWP([_ev("a"), _ev("b")])
    eng, push = FakeEngine(fail_ids=["a"]), FakePusher()
    result = run_once(wp, eng, push, NOW)
    assert [p["id"] for p in push.pushes] == ["b"]
    assert "b" in result and "a" not in result
