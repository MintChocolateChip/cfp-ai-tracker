import json
from pathlib import Path
from app.game_logic import GameState
from app.config import settings

DEMO_PATH = Path("demo_data/demo_events.json")

class DemoFeed:
    def __init__(self):
        self.idx = 0
        self.events = json.loads(DEMO_PATH.read_text(encoding="utf-8"))

    def set_index(self, i: int) -> None:
        try:
            i = int(i)
        except Exception:
            return
        if i < 0:
            i = 0
        if i > len(self.events):
            i = len(self.events)
        self.idx = i

    def get_index(self) -> int:
        return int(self.idx)

    def next_state(self) -> GameState:
        # idx points to the NEXT event to emit
        e = self.events[min(self.idx, len(self.events) - 1)]
        self.idx += 1
        return GameState(
            home_team=settings.home_team,
            away_team=settings.away_team,
            home_score=e.get("home_score", 0),
            away_score=e.get("away_score", 0),
            status=e.get("status", "pregame"),
            quarter=e.get("quarter"),
            clock=e.get("clock"),
            mendoza_pass_yds=e.get("mendoza_pass_yds"),
            mendoza_td=e.get("mendoza_td"),
            mendoza_int=e.get("mendoza_int"),
        )

_demo = DemoFeed()

def demo_get_index() -> int:
    return _demo.get_index()

def demo_set_index(i: int) -> None:
    _demo.set_index(i)

async def fetch_state() -> GameState:
    if settings.demo_mode:
        return _demo.next_state()
    return GameState(settings.home_team, settings.away_team)
