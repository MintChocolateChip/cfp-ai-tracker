import json
from pathlib import Path
import httpx
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


async def fetch_live_espn_state() -> GameState:
    """Fetch live game data from ESPN API."""
    if not settings.espn_game_id:
        # No game ID, return empty state
        return GameState(settings.home_team, settings.away_team)
    
    url = f"https://site.api.espn.com/apis/site/v2/sports/football/college-football/summary?event={settings.espn_game_id}"
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()
        
        # Parse ESPN data - use root level competitions (most reliable)
        competitions = data.get("competitions", [])
        if not competitions:
            # Fallback to header if root competitions not found
            header = data.get("header", {})
            competitions = header.get("competitions", [])
        
        if not competitions:
            # No competition data found
            return GameState(settings.home_team, settings.away_team)
        
        competition = competitions[0]
        competitors = competition.get("competitors", [])
        
        # Find home/away teams
        home_competitor = next((c for c in competitors if c.get("homeAway") == "home"), {})
        away_competitor = next((c for c in competitors if c.get("homeAway") == "away"), {})
        
        home_team = home_competitor.get("team", {}).get("displayName", settings.home_team)
        away_team = away_competitor.get("team", {}).get("displayName", settings.away_team)
        home_score = int(home_competitor.get("score", 0))
        away_score = int(away_competitor.get("score", 0))
        
        # Game status
        status_detail = competition.get("status", {})
        status_type = status_detail.get("type", {}).get("state", "pre").lower()
        
        # Map ESPN status to our status
        # ESPN uses: pre, in, post
        if status_type in ["pre", "scheduled"]:
            status = "pregame"
        elif status_type in ["in", "inprogress"]:
            status = "live"
        elif status_type in ["post", "final", "complete"]:
            status = "final"
        else:
            status = "pregame"
        
        # Quarter and clock
        period = status_detail.get("period")
        clock = status_detail.get("displayClock")
        
        # Player stats (tracked player)
        mendoza_pass_yds = None
        mendoza_td = None
        mendoza_int = None
        
        # Try to find player stats
        boxscore = data.get("boxscore", {})
        players_data = boxscore.get("players", [])
        
        for team_players in players_data:
            team_display = team_players.get("team", {}).get("displayName", "")
            stats_categories = team_players.get("statistics", [])
            for category in stats_categories:
                if category.get("name") == "passing":
                    athletes = category.get("athletes", [])
                    for athlete in athletes:
                        athlete_name = athlete.get("athlete", {}).get("displayName", "")
                        if settings.tracked_player.lower() in athlete_name.lower():
                            # Parse passing stats
                            stats = athlete.get("stats", [])
                            # ESPN API can return different formats:
                            # Short format: ['6/9', '62', '6.9', '0', '0'] = [comp/att, yards, avg, TD, INT]
                            # Long format: [comp, att, yards, avg, TD, INT, sacks, QBR]
                            
                            if len(stats) >= 5:
                                # Short format (more common)
                                try:
                                    mendoza_pass_yds = int(float(stats[1])) if stats[1] else None
                                    mendoza_td = int(float(stats[3])) if stats[3] else None
                                    mendoza_int = int(float(stats[4])) if stats[4] else None
                                except (ValueError, IndexError):
                                    pass
                            elif len(stats) >= 6:
                                # Long format (fallback)
                                try:
                                    mendoza_pass_yds = int(float(stats[2])) if stats[2] else None
                                    mendoza_td = int(float(stats[4])) if stats[4] else None
                                    mendoza_int = int(float(stats[5])) if stats[5] else None
                                except (ValueError, IndexError):
                                    pass
                            break
            if mendoza_pass_yds is not None:
                break
        
        return GameState(
            home_team=home_team,
            away_team=away_team,
            home_score=home_score,
            away_score=away_score,
            status=status,
            quarter=period,
            clock=clock,
            mendoza_pass_yds=mendoza_pass_yds,
            mendoza_td=mendoza_td,
            mendoza_int=mendoza_int,
        )
    
    except Exception as e:
        print(f"Error fetching live data from ESPN: {e}")
        # Return default state on error
        return GameState(settings.home_team, settings.away_team)


async def fetch_state() -> GameState:
    if settings.demo_mode:
        return _demo.next_state()
    return await fetch_live_espn_state()
