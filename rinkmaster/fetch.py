"""Seiten-Discovery (nav.html) und Laden der Rinkmaster-Seiten.

Netzwerk ist über den injizierbaren ``getter`` von der Logik getrennt, damit
Tests gegen lokale Fixtures laufen können.
"""
from __future__ import annotations

import urllib.request
from typing import Callable

from bs4 import BeautifulSoup


def http_get(url: str, timeout: int = 15) -> str | None:
    """Lädt eine URL; gibt None bei 404/Fehler zurück."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "rinkmaster-engine"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if getattr(resp, "status", 200) != 200:
                return None
            return resp.read().decode("utf-8", errors="replace")
    except Exception:
        return None


def discover(nav_html: str) -> dict:
    """Liest nav.html als Inhaltsverzeichnis.

    Rückgabe: ``{"rankings": [{"id","label","page"}...],
    "teams_page": str|None, "current_page": str|None}``.
    """
    soup = BeautifulSoup(nav_html, "html.parser")
    rankings = []
    for row in soup.select(".grid .row.ranking"):
        link = row.select_one(".ranking a")
        if not link:
            continue
        holder = link.find_parent(class_="ranking")
        rankings.append({
            "id": holder.get("id") if holder else None,
            "label": link.get_text(strip=True),
            "page": link.get("href"),
        })
    teams = soup.select_one("#teams a")
    current = soup.select_one("#current a")
    return {
        "rankings": rankings,
        "teams_page": teams.get("href") if teams else None,
        "current_page": current.get("href") if current else None,
    }


def load_pages(base_url: str, getter: Callable[[str], str | None] = http_get) -> dict[str, str | None]:
    """Holt nav.html über ``getter``, ermittelt den Seitensatz und lädt jede
    gefundene Seite. 404/None wird toleriert und als None übernommen."""
    nav = getter(base_url + "nav.html")
    if nav is None:
        return {}
    disc = discover(nav)
    names: list[str] = [r["page"] for r in disc["rankings"] if r["page"]]
    if disc["teams_page"]:
        names.append(disc["teams_page"])
    if disc["current_page"]:
        names.append(disc["current_page"])
    pages: dict[str, str | None] = {}
    for name in names:
        if name not in pages:
            pages[name] = getter(base_url + name)
    return pages
