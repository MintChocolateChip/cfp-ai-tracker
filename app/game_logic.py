from dataclasses import dataclass
import hashlib
import json
from datetime import datetime, timezone

@dataclass
class GameState:
    home_team: str
    away_team: str
    home_score: int = 0
    away_score: int = 0
    status: str = "pregame"     # pregame | live | final
    quarter: int | None = None
    clock: str | None = None

    mendoza_pass_yds: int | None = None
    mendoza_td: int | None = None
    mendoza_int: int | None = None

    def to_dict(self) -> dict:
        return {
            "home_team": self.home_team,
            "away_team": self.away_team,
            "home_score": self.home_score,
            "away_score": self.away_score,
            "status": self.status,
            "quarter": self.quarter,
            "clock": self.clock,
            "mendoza": {
                "pass_yds": self.mendoza_pass_yds,
                "td": self.mendoza_td,
                "int": self.mendoza_int,
            },
        }

# Fingerprinting detects *state transitions*, not time-based polling.
# This mirrors edge-triggered logic in digital systems.
def fingerprint(state: GameState) -> str:
    payload = {
        "home_score": state.home_score,
        "away_score": state.away_score,
        "status": state.status,
        "quarter": state.quarter,
        "clock": state.clock,
        "mendoza": (state.mendoza_pass_yds, state.mendoza_td, state.mendoza_int),
    }
    b = json.dumps(payload, sort_keys=True).encode("utf-8")
    return hashlib.sha256(b).hexdigest()

# Explainable heuristic model (not ML):
# deterministic, bounded, debuggable.
def compute_win_prob_simple(state: GameState) -> float:
    import math
    margin = (state.home_score or 0) - (state.away_score or 0)
    q = state.quarter or 1
    time_weight = {1: 0.8, 2: 1.0, 3: 1.2, 4: 1.4}.get(q, 1.0)
    x = margin * 0.18 * time_weight
    p = 1 / (1 + math.exp(-x))
    return float(max(0.01, min(0.99, p)))

def kickoff_countdown(kickoff_iso: str) -> dict:
    kickoff = datetime.fromisoformat(kickoff_iso)
    now = datetime.now(tz=kickoff.tzinfo or timezone.utc)
    diff = kickoff - now
    seconds = max(0, int(diff.total_seconds()))
    return {
        "h": seconds // 3600,
        "m": (seconds % 3600) // 60,
        "s": seconds % 60,
        "seconds": seconds,
    }

# Explicit finite-state-machine label
def game_phase(state: GameState) -> str:
    if state.status == "final":
        return "FINAL"
    if state.status == "live":
        return "LIVE"
    return "PREGAME"
