"""Entrypoint des Cloud-Runners: python -m runner [--dry-run].

Liest aktive Events aus WordPress, parst die faelligen mit der Engine und pusht sie zurueck.
--dry-run liest + parst nur (kein Push, kein Clear, keine Auth noetig).
Exit-Code 0 auch wenn einzelne Events fehlschlugen (Fehler werden je Event isoliert geloggt).
"""
import argparse
import sys
from datetime import datetime, timezone

from runner.engine_cli import EngineRunner
from runner.orchestrate import run_once
from runner.selection import events_to_refresh
from runner.wp_client import WpClient, auth_from_env

DEFAULT_BASE = "https://slocurling.ch/wp-json/rinkmaster/v1"


def main(argv=None):
    parser = argparse.ArgumentParser(prog="runner", description="Rinkmaster Cloud-Runner")
    parser.add_argument("--dry-run", action="store_true", help="nur lesen + parsen, nicht pushen")
    parser.add_argument("--base", default=None, help="REST-Base (sonst WP_BASE oder Default)")
    args = parser.parse_args(argv)

    import os
    base = args.base or os.environ.get("WP_BASE", DEFAULT_BASE)
    client = WpClient(base, auth_from_env())
    engine = EngineRunner()
    now = datetime.now(timezone.utc)

    if args.dry_run:
        events, interval, refresh = client.fetch_state()
        due = events_to_refresh(events, interval, now, refresh)
        print("[runner] dry-run: %d Events, Intervall %d Min, refresh=%s, faellig: %s"
              % (len(events), interval, refresh, due))
        by_id = {e["id"]: e for e in events}
        for event_id in due:
            e = by_id[event_id]
            data = engine.build(url=e["url"], id=e["id"], name=e.get("name", ""),
                                season=e.get("saison", ""), live=bool(e.get("live")))
            n = len(data.get("games", [])) if isinstance(data, dict) else "?"
            print("[runner] dry-run: %s geparst, %s Spiele (nicht gepusht)" % (event_id, n))
        return 0

    refreshed = run_once(client, engine, client, now)
    print("[runner] aufgefrischt: %s" % refreshed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
