#!/usr/bin/env python3
"""
Debug script to see the actual ESPN API response structure.
"""
import asyncio
import httpx
import json
import sys

async def fetch_and_debug(game_id):
    url = f"https://site.api.espn.com/apis/site/v2/sports/football/college-football/summary?event={game_id}"
    
    print(f"\n{'='*80}")
    print(f"Fetching ESPN API for game ID: {game_id}")
    print(f"URL: {url}")
    print(f"{'='*80}\n")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()
        
        # Save full response
        with open("espn_response.json", "w") as f:
            json.dump(data, f, indent=2)
        print("✅ Full response saved to espn_response.json\n")
        
        # Show key structures
        print("="*80)
        print("KEY DATA STRUCTURES")
        print("="*80)
        
        # Check header
        if "header" in data:
            print("\n📋 HEADER:")
            print(f"  - Keys: {list(data['header'].keys())}")
            
            if "competitions" in data["header"]:
                print(f"\n  📊 header.competitions:")
                comp = data["header"]["competitions"][0]
                print(f"    - Keys: {list(comp.keys())}")
                
                if "competitors" in comp:
                    print(f"\n    👥 Competitors (from header):")
                    for c in comp["competitors"]:
                        print(f"      - {c.get('team', {}).get('displayName', '?')}: {c.get('score', '?')}")
                
                if "status" in comp:
                    status = comp["status"]
                    print(f"\n    ⏰ Status:")
                    print(f"      - Type: {status.get('type', {}).get('name', '?')}")
                    print(f"      - Period: {status.get('period', '?')}")
                    print(f"      - Clock: {status.get('displayClock', '?')}")
        
        # Check boxscore
        if "boxscore" in data:
            print(f"\n📦 BOXSCORE:")
            print(f"  - Keys: {list(data['boxscore'].keys())}")
            
            if "teams" in data["boxscore"]:
                print(f"\n  🏈 Teams in boxscore:")
                for team in data["boxscore"]["teams"]:
                    print(f"    - {team.get('team', {}).get('displayName', '?')}")
                    print(f"      Score: {team.get('statistics', [{}])[0].get('displayValue', '?') if team.get('statistics') else 'N/A'}")
        
        # Check for scoringPlays
        if "scoringPlays" in data:
            print(f"\n⚽ SCORING PLAYS: {len(data['scoringPlays'])} plays")
        
        # Most reliable: competitions at root level
        if "competitions" in data:
            print(f"\n🎯 ROOT COMPETITIONS (Most reliable!):")
            comp = data["competitions"][0]
            print(f"  - Keys: {list(comp.keys())}")
            
            if "competitors" in comp:
                print(f"\n  👥 Competitors:")
                for c in comp["competitors"]:
                    team = c.get("team", {}).get("displayName", "?")
                    score = c.get("score", "?")
                    home_away = c.get("homeAway", "?")
                    print(f"    - {team} ({home_away}): {score}")
            
            if "status" in comp:
                status = comp["status"]
                print(f"\n  ⏰ Status:")
                print(f"    - State: {status.get('type', {}).get('state', '?')}")
                print(f"    - Detail: {status.get('type', {}).get('detail', '?')}")
                print(f"    - Period: {status.get('period', '?')}")
                print(f"    - Clock: {status.get('displayClock', '?')}")
        
        print(f"\n{'='*80}")
        print("Check espn_response.json for full details")
        print(f"{'='*80}\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python debug_espn_api.py <ESPN_GAME_ID>")
        print("\nExample: python debug_espn_api.py 401635594")
        sys.exit(1)
    
    game_id = sys.argv[1]
    asyncio.run(fetch_and_debug(game_id))
