"""WordPress-REST-Client fuer den Runner. Nur Stdlib (urllib)."""
import base64
import json
import os
import urllib.parse
import urllib.request
from datetime import datetime


def auth_from_env():
    """Authorization-Header aus der Umgebung: WP_AUTH direkt, sonst Basic aus WP_USER/WP_APP_PASSWORD."""
    direct = os.environ.get("WP_AUTH")
    if direct and direct.strip():
        return direct.strip()
    user = os.environ.get("WP_USER")
    pw = os.environ.get("WP_APP_PASSWORD")
    if user and pw:
        token = base64.b64encode(("%s:%s" % (user.strip(), pw.strip())).encode("utf-8")).decode("ascii")
        return "Basic " + token
    return None


class WpClient:
    """Erfuellt sowohl das wp- (fetch_state/clear_refresh) als auch das pusher-Protokoll (push)."""

    def __init__(self, base, auth=None):
        self.base = base.rstrip("/")
        self.auth = auth

    def _req(self, method, path, params=None, body=None, auth=False):
        url = self.base + path
        if params:
            url += "?" + urllib.parse.urlencode(params)
        data = body.encode("utf-8") if isinstance(body, str) else body
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("Content-Type", "application/json; charset=utf-8")
        if auth:
            if not self.auth:
                raise RuntimeError("Keine WP-Auth gesetzt (WP_AUTH oder WP_USER/WP_APP_PASSWORD).")
            req.add_header("Authorization", self.auth)
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode("utf-8")
        return json.loads(raw) if raw else None

    def fetch_state(self):
        d = self._req("GET", "/events")
        events = []
        for e in (d.get("events") or []):
            lu = e.get("last_updated")
            e2 = dict(e)
            e2["last_updated"] = datetime.fromisoformat(lu) if lu else None
            events.append(e2)
        interval = int((d.get("settings") or {}).get("interval_min", 10))
        return (events, interval, bool(d.get("refresh_requested")))

    def clear_refresh(self):
        self._req("POST", "/refresh", params={"clear": 1}, body="", auth=True)

    def push(self, event_id, data, views=None):
        body = data if isinstance(data, str) else json.dumps(data, ensure_ascii=False)
        return self._req("POST", "/data", params={"event": event_id}, body=body, auth=True)
