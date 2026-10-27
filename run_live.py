import sys, os, json
os.chdir(r"C:\Users\pjun\OneDrive\ClaudeCode\rinkmaster-engine")
sys.path.insert(0, r"C:\Users\pjun\OneDrive\ClaudeCode\rinkmaster-engine")
from rinkmaster.build import _cli
_cli([
    "--base-url", "https://results.curling-stgallen.ch/26_27/slo/",
    "--id", "slo", "--name", "Superliga Ostschweiz", "--season", "2026/27",
    "--out", r"C:\Users\pjun\OneDrive\ClaudeCode\slocurling-ch\build-scripts\slo.json",
    "--live",
])
# Status ausgeben
data = json.load(open(r"C:\Users\pjun\OneDrive\ClaudeCode\slocurling-ch\build-scripts\slo.json", encoding="utf-8"))
live = [g for g in data["games"] if g["status"] == "live"]
final = [g for g in data["games"] if g["status"] == "final"]
print(f"live={data['live']}, live_games={len(live)}, final_games={len(final)}, last_update={data.get('last_update')}")
for g in live:
    t = g["teams"]
    print(f"  Rink {g['rink']}: {t[0]['name']} {t[0]['total']} vs {t[1]['total']} {t[1]['name']}, end={g['current_end']}")
