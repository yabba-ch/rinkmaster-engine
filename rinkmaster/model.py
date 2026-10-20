"""Datenmodell und JSON-Serialisierung für ein Rinkmaster-Turnier."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field


@dataclass
class Player:
    name: str
    position: str | None = None   # roh aus Rinkmaster, z.B. "Nr. 4", "Alt."
    role: str | None = None       # abgeleitet: Lead/Second/Third/Skip/Ersatz
    is_skip: bool = False


@dataclass
class Team:
    id: str
    name: str
    club: str | None = None
    skip_name: str | None = None
    players: list[Player] = field(default_factory=list)
    rank: int | None = None
    points: int | None = None
    ends: int | None = None
    stones: int | None = None


@dataclass
class GameTeam:
    name: str
    stone_color: str | None = None
    total: int | None = None
    ends: list[int | None] = field(default_factory=list)


@dataclass
class Game:
    number: int | None = None
    round: int | None = None
    date: str | None = None
    time: str | None = None
    venue: str | None = None
    rink: str | None = None
    status: str = "next"          # next | live | final
    hammer_team: str | None = None
    teams: list[GameTeam] = field(default_factory=list)
    current_end: int | None = None


@dataclass
class RankingRow:
    rank: int | None
    team_id: str | None
    team_name: str
    points: int | None = None
    ends: int | None = None
    stones: int | None = None
    pt_dir: int | None = None
    played: int | None = None


@dataclass
class Ranking:
    id: str
    label: str
    rows: list[RankingRow] = field(default_factory=list)


@dataclass
class Tournament:
    id: str
    name: str
    season: str | None = None
    last_update: str | None = None
    live: bool = False
    teams: list[Team] = field(default_factory=list)
    rankings: list[Ranking] = field(default_factory=list)
    games: list[Game] = field(default_factory=list)


def to_json(tournament: Tournament) -> str:
    """Serialisiert ein Tournament als UTF-8-JSON (Umlaute bleiben erhalten)."""
    return json.dumps(asdict(tournament), ensure_ascii=False, indent=2)
