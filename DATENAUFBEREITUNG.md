# Curling Rinkmaster — Datenaufbereitung (Engine-Vorgabe)

> Verbindliche Vorgabe für **`rinkmaster-engine`**: welches JSON die Engine liefert, mit welchen Entscheidungen, Feldern und Regeln.
> **Konsument:** der Renderer + das Live-Widget auf **slocurling.ch**. Dessen Gegenstück ist `slocurling-ch/build-scripts/rinkmaster-elemente-richtlinie.md`.
> **Schnittstelle zwischen beiden Projekten ist allein dieses JSON** — kein HTML, kein CSS, keine Darstellungs-Strings.
>
> Stand 2026-10-22. Abschnitte: Grundsatz · JSON-Vertrag (Ist) · Entscheidungen (Soll) · Feld→Klasse · Regeln · Workflow · Prüf-Checkliste.

---

## 1. Grundsatz / Architektur-Entscheidung

- Die Engine liefert **site-neutrales JSON**, genau **eine Datei pro Turnier** (`<id>.json`, z. B. `slo.json`).
- **Keine** HTML-Fragmente, **keine** CSS-Klassen, **keine** deutschen Darstellungs-Strings (z. B. Wochentag „Mo."). Alles Darstellungsnahe — Wochentag, Namensaufteilung, `–`/`·`-Glyphen, Platzierungs-Abzeichen — macht der **Renderer** auf der Site.
- **Veröffentlichung:** als statische Datei über **GitHub Pages** (HTTPS, sendet `Access-Control-Allow-Origin: *`). Das Live-Widget lädt genau diese **stabile URL**. Kein eigener Server, keine API.
- **Schema-Stabilität:** Änderungen möglichst **additiv** (neue Felder dürfen dazukommen, bestehende nicht umbenannt/entfernt werden). Für Brüche dient das Feld `schema` (Versionsnummer, Entscheidung **E5**).
- UTF-8, Umlaute bleiben erhalten (`json.dumps(..., ensure_ascii=False, indent=2)` — ist bereits so in `model.to_json`).

---

## 2. JSON-Vertrag (Ist-Stand — `rinkmaster/model.py`)

Top-Level-Objekt **`Tournament`**:

```jsonc
{
  "schema": 1,                    // JSON-Schema-Version (E5), immer erster Schlüssel
  "id": "slo",
  "name": "Superliga Ostschweiz",
  "season": "2026/27",            // optional
  "last_update": "22.10.2026 / 20:14",       // Rohtext aus "Spielstand vom:", kann null sein
  "last_update_iso": "2026-10-22T20:14:00",  // ISO, naive lokal (E4), kann null sein
  "live": false,                  // true, wenn Live-Lauf
  "teams":    [ Team, … ],
  "rankings": [ Ranking, … ],     // rankings[0] = Hauptrangliste
  "games":    [ Game, … ]         // chronologisch, number = 1..N
}
```

**`Team`**

| Feld | Typ | Herkunft / Bedeutung |
|---|---|---|
| `id` | str | `a[id^='team']` aus `m.html`, z. B. `team1` — **Join-Schlüssel** |
| `name` | str | voller Titel, i. d. R. `«Club / Teamname»` |
| `club` | str\|null | Teil **vor** `" / "` |
| `skip_name` | str\|null | Spieler mit `(Skip)` |
| `players` | Player[] | Aufstellung inkl. Ersatz |
| `rank` / `points` / `ends` / `stones` | int\|null | aus `rankings[0]` je `team_id` übernommen (siehe `build.py`) |

**`Player`**

| Feld | Typ | Bedeutung |
|---|---|---|
| `name` | str | ohne `(Skip)`-Zusatz |
| `position` | str\|null | roh, z. B. `"Nr. 4"`, `"Alt."` |
| `role` | str\|null | abgeleitet: `Lead`/`Second`/`Third`/`Skip`/`Ersatz` (`ROLE_MAP`) |
| `is_skip` | bool | `(Skip)` im Rohtext |

**`Ranking`** / **`RankingRow`**

| Feld | Typ | Bedeutung |
|---|---|---|
| `Ranking.id` / `Ranking.label` | str | Ranglisten-Kennung/-Titel |
| `Ranking.rows` | RankingRow[] | Zeilen |
| `RankingRow.rank` | int\|null | Platz (null = unplatziert → Renderer zeigt «–») |
| `RankingRow.team_id` | str\|null | **Join** auf `Team.id` (für `skip_name`) |
| `RankingRow.team_name` | str | Anzeigename der Zeile |
| `RankingRow.points` / `ends` / `stones` / `pt_dir` / `played` | int\|null | Kennzahlen (Site zeigt nur `points` + `stones`) |

**`Game`** / **`GameTeam`**

| Feld | Typ | Bedeutung |
|---|---|---|
| `Game.number` | int\|null | **stabile** fortlaufende Spielnummer (`numbering.py`, chronologisch) |
| `Game.round` | int\|null | Runde |
| `Game.date` | str\|null | **`dd.mm.yyyy`** (aus `parse_meta`) |
| `Game.date_iso` | str\|null | **`yyyy-mm-dd`** aus `date` (E2 ✓ 2026-10-22) |
| `Game.time` | str\|null | `HH:MM` |
| `Game.venue` | str\|null | Spielort/Halle |
| `Game.rink` | str\|null | Bahn |
| `Game.status` | str | **`next` \| `live` \| `final`** |
| `Game.hammer_team` | str\|null | = `GameTeam.name` des Teams mit Hammer (`*`) |
| `Game.current_end` | int\|null | laufendes End (nur `live`) |
| `Game.teams` | GameTeam[] | **2 Einträge**, Reihenfolge = Rinkmaster-Reihenfolge |
| `GameTeam.name` | str | Teamname |
| `GameTeam.stone_color` | str\|null | **`"yellow"`/`"red"` positional** (E1 ✓ 2026-10-22) |
| `GameTeam.total` | int\|null | Total |
| `GameTeam.ends` | (int\|null)[] | **Länge 9** = Ends 1–8 + Zusatzend (ZE). Ziffer→int, leer/`X`→null |

---

## 3. Entscheidungen (Soll — in der Engine umzusetzen)

Diese Punkte fehlen oder sind unvollständig und sind für den Site-Konsum nötig. **Stand 2026-10-22: E1–E5 alle umgesetzt.**

**E1 — `stone_color` befüllen. ✓ erledigt 2026-10-22.** Positional in `build._normalize_games`: `teams[0]="yellow"`, `teams[1]="red"` (bereits gesetzte Werte werden nicht überschrieben). Renderer mappt auf `stein--gelb/--rot`.

**E2 — `date_iso` ergänzen. ✓ erledigt 2026-10-22.** Feld `Game.date_iso` = `"yyyy-mm-dd"`, abgeleitet via `util.to_iso_date` (null wenn unparsbar). Macht die **Wochentags**-Berechnung im Renderer eindeutig.

**E3 — Live-Parser (`a.html`). ✓ erledigt 2026-10-22, verifiziert 2026-10-26.** `rinkmaster/parse_live.py` liest den Container **`.table.current`**. Die Spiel-Blöcke tragen die Klasse **`.result`** (nicht `.scoreebe` wie im Resultate-Container), innere Struktur identisch → `parse_scoreebe` wiederverwendet. Header-Zelle: **`.cell.title`** (nicht `.cell.plan`). Rink-Label enthält Suffix «` - Spiel läuft`», der Parser schneidet ihn ab. `status="live"`, offene Ends als `null`. In `build_tournament` wird a.html über `discovery["current_page"]` mitgeparst und per `game_key` gemergt (Präzedenz **final > live > next**, `_dedupe`).
  - **`current_end` ist abgeleitet** (`_current_end`): höchste End-Nummer mit einem Wert **+ 1** = das derzeit gespielte End. Rinkmaster liefert keinen expliziten Marker in a.html. Mindestens 1, maximal 9 (ZE). An echtem Live-Spiel (2026-10-26) verifiziert.
  - Leerer Stand (`<div class="table current"><div class="comment">…keine aktuellen Resultate…</div></div>`) → keine Live-Spiele.

**E4 — `last_update_iso` ergänzen. ✓ erledigt 2026-10-22.** `util.to_iso_datetime` leitet aus `last_update` einen ISO-Zeitstempel ab — **naive lokale Zeit ohne Offset** (`"2026-10-19T22:22:47"`), bewusst ohne Zeitzonen-Abhängigkeit, da Site und Daten Schweizer Zeit sind. Fürs Live-Widget („Spielstand vom …", Alters-Check).

**E5 — `schema`-Version voranstellen. ✓ erledigt 2026-10-22.** Top-Level `"schema": 1`, in `to_json` immer als erster Schlüssel ausgegeben. Das Live-Widget kann so bei einem Schemabruch sauber auf den Fallback gehen.

**E6 — (optional) Felder behalten.** `pt_dir`, `ends`, `played`, `season` bleiben im JSON, auch wenn die Site sie nicht zeigt — spätere Views/Events können sie nutzen. *Keine Aktion, nur festhalten.*

> Alle Soll-Felder sind **additiv** → kein Bruch für einen Konsumenten, der sie noch nicht liest.

---

## 4. Feld → Site-Klasse (Konsum-Übersicht)

Nur zur Orientierung — die **maßgebliche** Zuordnung steht in der Site-Richtlinie. Die Engine liefert die Rohwerte, der Renderer vergibt die Klassen.

| JSON | Site-Klasse (Renderer) |
|---|---|
| `Game.number` / `round` | `.scoreboard-spiel` / `.spiel-nr` |
| `venue` + `date`(→Wochentag) + `time` + `rink` | `.scoreboard-meta` |
| `status=live` + `current_end` | `.scoreboard-kopf--live`, `.badge--live` > `.livepunkt`, `.sb-kopfzelle--aktuell` |
| `GameTeam.stone_color` | `.stein--gelb` / `.stein--rot` |
| `GameTeam.name` | `.sb-teamname` / `.spiel-team` |
| `hammer_team` | `.hammer` «Hammer» |
| `GameTeam.ends[i]` | `.sb-wert` (oben) / `.sb-wert--zeile` (unten); null → `.sb-wert--leer` mit `–`/`·` |
| `GameTeam.total` | `.sb-tot` (+ `--sieger` bei `final`-Gewinner) |
| `RankingRow.rank` | `.rang-abzeichen` (`--1/--2/--3`) |
| `RankingRow.team_name` + join→`skip_name` | `.rl-teamname` + `.rl-skip` |
| `RankingRow.points` / `stones` | `.rl-pkt` / `.rl-wert` |
| `Team.club` / Name-nach-`/` | `.team-club` / `h3.team-name` |
| `Player.role` / `name` / `is_skip` | `.spieler-pos` / `.spieler-name` / `.skip-abzeichen` |
| `Player.role=Ersatz` | «Ersatz»-Liste in `.team-sponsoren` |

---

## 5. Regeln & Abgrenzung

- **Nie aus der Engine (manuell auf der Site):** Team-Sponsoren. Die Engine kennt sie nicht und darf kein Sponsorfeld erfinden.
- **Steinfarbe:** Engine vergibt positional (E1). Werte `"yellow"`/`"red"`.
- **Spielnummern:** stabil über `numbering.assign_numbers` + `game_key` (team-reihenfolge-unabhängig) — ein Spiel behält seine Nummer beim Wechsel „nächstes Spiel → Resultat". Nicht ändern.
- **Ends:** immer Liste der **Länge 9** (Ends 1–8 + ZE). `null` = blank/`X`. Die Unterscheidung `–` (gespielt-blank) vs `·` (noch nicht gespielt) trifft der **Renderer** anhand `status`/`current_end` — die Engine liefert nur `null`.
- **`status`:** `next` (Spielplan), `live` (Live-Scoreboard, braucht E3), `final` (fertiges Scoreboard).
- **`hammer_team`:** exakt gleich einem der beiden `GameTeam.name` oder `null`.
- **Rangliste:** `rankings[0]` ist die Hauptrangliste (von der Site gezeigt). `skip_name` steht **nicht** in `RankingRow` → Konsument joint über `team_id` auf `teams[]`.
- **Team-Anzeigename:** Engine liefert `name` (voll) + `club`; der Renderer zeigt den Teil **nach** `" / "`.

---

## 6. Workflow / CLI

```bash
python -m rinkmaster.build \
  --base-url https://<rinkmaster-host>/<pfad>/ \
  --id slo --name "Superliga Ostschweiz" \
  [--season "2026/27"] [--live] \
  --out slo.json
```

- Liest `nav.html` (Discovery der Ranglisten/Teams-Seite), dann alle Seiten unter `--base-url` (`fetch.load_pages`).
- `--live` setzt `Tournament.live=true` (Flag für den Live-Lauf). Laufende Spiele liest `parse_live` aus `a.html` unabhängig vom Flag, sobald die Seite welche enthält (E3 ✓).
- **Lokal ausführen** (nicht über einen VPS/Rechenzentrum) — analog zur `/watch`-Regel.
- Ergebnis `slo.json` → in das **GitHub-Pages**-Repo committen/veröffentlichen; die Live-URL bleibt stabil.

---

## 7. Prüf-Checkliste (Engine, vor jeder Veröffentlichung)

1. Valides **UTF-8-JSON**, `ensure_ascii=False`, Umlaute intakt.
2. Jedes `Team` hat eine nicht-leere `id`; `rankings[0]` vorhanden (sofern eine Rangliste existiert).
3. `Game.number` eindeutig `1..N` und **stabil** gegenüber dem Vorlauf (gleiches Spiel = gleiche Nummer).
4. `GameTeam.ends` hat **Länge 9**; Werte int oder null.
5. `stone_color` gesetzt (nach **E1**), `date_iso` gesetzt (nach **E2**).
6. `status` nur aus {`next`,`live`,`final`}; `current_end` nur bei `live`.
7. `hammer_team` matcht einen `GameTeam.name` oder ist null.
8. Keine Darstellungs-Strings (kein Wochentag, keine HTML-Entities, keine CSS-Klassen) im JSON.
