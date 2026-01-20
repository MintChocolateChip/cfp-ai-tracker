#!/usr/bin/env python3
"""
Test script to verify ESPN API integration works correctly.
This helps debug live data fetching before running the full app.
"""
import asyncio
import os
import sys

# Set environment for testing
os.environ["DEMO_MODE"] = "0"
os.environ["ESPN_GAME_ID"] = sys.argv[1] if len(sys.argv) > 1 else ""

if not os.environ["ESPN_GAME_ID"]:
    print("Usage: python test_espn_live.py <ESPN_GAME_ID>")
    print("\nExample: python test_espn_live.py 401635594")
    print("\nRun 'python find_live_games.py' to find game IDs")
    sys.exit(1)

from app.data_sources import fetch_live_espn_state


async def main():
    print(f"\n{'='*80}")
    print(f"Testing ESPN API Integration")
    print(f"{'='*80}\n")
    print(f"Game ID: {os.environ['ESPN_GAME_ID']}")
    print("\nFetching game data...\n")
    
    try:
        state = await fetch_live_espn_state()
        
        print(f"✅ Successfully fetched game data!\n")
        print(f"{'='*80}")
        print(f"GAME STATE")
        print(f"{'='*80}")
        print(f"Status: {state.status}")
        print(f"Teams: {state.away_team} @ {state.home_team}")
        print(f"Score: {state.away_score} - {state.home_score}")
        
        if state.quarter:
            print(f"Quarter: {state.quarter}")
        if state.clock:
            print(f"Clock: {state.clock}")
        
        print(f"\n{'='*80}")
        print(f"PLAYER STATS")
        print(f"{'='*80}")
        
        if state.mendoza_pass_yds is not None:
            print(f"Passing Yards: {state.mendoza_pass_yds}")
        else:
            print(f"Passing Yards: Not found")
            
        if state.mendoza_td is not None:
            print(f"Touchdowns: {state.mendoza_td}")
        else:
            print(f"Touchdowns: Not found")
            
        if state.mendoza_int is not None:
            print(f"Interceptions: {state.mendoza_int}")
        else:
            print(f"Interceptions: Not found")
        
        if None in (state.mendoza_pass_yds, state.mendoza_td, state.mendoza_int):
            print(f"\n⚠️  Player stats not found. This could mean:")
            print(f"   - Player '{os.environ.get('TRACKED_PLAYER', 'Fernando Mendoza')}' is not in the game")
            print(f"   - Player hasn't recorded any stats yet")
            print(f"   - Player name doesn't match ESPN roster")
        
        print(f"\n{'='*80}")
        print(f"✅ Test complete!")
        print(f"{'='*80}\n")
        
    except Exception as e:
        print(f"\n❌ Error fetching game data:")
        print(f"   {type(e).__name__}: {e}")
        print(f"\nTroubleshooting:")
        print(f"   - Verify the game ID is correct")
        print(f"   - Check your internet connection")
        print(f"   - Ensure the game exists in ESPN's database")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
