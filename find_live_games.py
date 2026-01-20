#!/usr/bin/env python3
"""
Helper script to find live college football games and their ESPN game IDs.
Run this to see what games are happening now and get the game ID to use.
"""
import httpx
import asyncio
from datetime import datetime


async def find_live_games():
    """Fetch current college football games from ESPN."""
    url = "https://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard"
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()
        
        events = data.get("events", [])
        
        if not events:
            print("No college football games found at this time.")
            return
        
        print(f"\n{'='*80}")
        print(f"College Football Games - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*80}\n")
        
        for event in events:
            game_id = event.get("id")
            name = event.get("name", "Unknown")
            short_name = event.get("shortName", "")
            status = event.get("status", {})
            status_type = status.get("type", {}).get("state", "pre")
            status_detail = status.get("type", {}).get("detail", "Scheduled")
            
            competitions = event.get("competitions", [{}])[0]
            competitors = competitions.get("competitors", [])
            
            home = next((c for c in competitors if c.get("homeAway") == "home"), {})
            away = next((c for c in competitors if c.get("homeAway") == "away"), {})
            
            home_team = home.get("team", {}).get("displayName", "?")
            away_team = away.get("team", {}).get("displayName", "?")
            home_score = home.get("score", 0)
            away_score = away.get("score", 0)
            
            # Status indicator
            if status_type == "in":
                status_icon = "🔴 LIVE"
            elif status_type == "post":
                status_icon = "✅ FINAL"
            else:
                status_icon = "⏰ SCHEDULED"
            
            print(f"{status_icon} {short_name}")
            print(f"  Game ID: {game_id}")
            print(f"  {away_team} @ {home_team}")
            print(f"  Score: {away_score} - {home_score}")
            print(f"  Status: {status_detail}")
            
            # Show period/clock if live
            if status_type == "in":
                period = status.get("period")
                clock = status.get("displayClock", "")
                print(f"  Q{period} - {clock}")
            
            print()
        
        print(f"\nTo track a live game, set: ESPN_GAME_ID={events[0].get('id')}")
        print(f"And set: DEMO_MODE=0")
        print()
    
    except Exception as e:
        print(f"Error fetching games: {e}")


if __name__ == "__main__":
    asyncio.run(find_live_games())
