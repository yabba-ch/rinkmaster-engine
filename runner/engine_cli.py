"""Engine-Aufruf fuer den Runner: ruft die bestehende CLI `python -m rinkmaster.build` je Event auf."""
import json
import os
import subprocess
import sys
import tempfile

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class EngineRunner:
    def __init__(self, python=None):
        self.python = python or sys.executable

    def build(self, url, id, name, season, live):
        """Parst ein Event ueber die Engine-CLI und gibt das JSON als dict zurueck."""
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "data.json")
            cmd = [self.python, "-m", "rinkmaster.build",
                   "--base-url", url, "--id", id, "--name", name,
                   "--season", season, "--out", out]
            if live:
                cmd.append("--live")
            subprocess.run(cmd, check=True, cwd=REPO_ROOT, capture_output=True, text=True)
            with open(out, encoding="utf-8") as fh:
                return json.load(fh)
