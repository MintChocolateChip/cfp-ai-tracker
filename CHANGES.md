# Live Data Integration - Changes Summary

## What Was Changed

This update adds **live game tracking** capabilities to the CFP AI Tracker, allowing it to fetch real-time game data from ESPN's API instead of just using pre-recorded demo data.

## Modified Files

### 1. `app/config.py`
**Added:**
- `espn_game_id`: ESPN game ID for live tracking
- `tracked_player`: Configurable player name (default: "Fernando Mendoza")

**Usage:**
```python
settings.espn_game_id = "401635594"
settings.tracked_player = "Fernando Mendoza"
```

### 2. `app/data_sources.py`
**Added:**
- `fetch_live_espn_state()`: New async function to fetch live data from ESPN API
  - Fetches game summary from ESPN API
  - Parses score, quarter, clock, game status
  - Extracts player passing stats (yards, TDs, INTs)
  - Handles errors gracefully

**Modified:**
- `fetch_state()`: Now routes to `fetch_live_espn_state()` when `DEMO_MODE=0`

**ESPN API Used:**
```
https://site.api.espn.com/apis/site/v2/sports/football/college-football/summary?event={game_id}
```

### 3. `app/main.py`
**Modified:**
- Removed hardcoded `PLAYER_NAME` constant
- Now uses `settings.tracked_player` for player tracking
- Fully configurable via environment variables

### 4. `README.md`
**Updated:**
- Added live game tracking instructions
- Included ESPN API integration details
- Added quick start guide
- Documented demo vs live mode

## New Files Created

### 1. `find_live_games.py`
**Purpose:** Helper script to discover live college football games

**Features:**
- Fetches all current games from ESPN
- Shows game IDs, scores, and status
- Displays live game indicator (🔴 LIVE)
- Easy copy-paste game IDs

**Usage:**
```bash
python find_live_games.py
```

### 2. `test_espn_live.py`
**Purpose:** Test ESPN API integration before running full app

**Features:**
- Validates ESPN API connection
- Shows parsed game data
- Displays player stats if found
- Helpful error messages

**Usage:**
```bash
python test_espn_live.py 401635594
```

### 3. `SETUP.md`
**Purpose:** Comprehensive setup and configuration guide

**Contents:**
- Environment variable reference
- Installation troubleshooting
- ESPN API details
- Common issues and fixes

### 4. `QUICKSTART.md`
**Purpose:** 5-minute quick start guide

**Contents:**
- Step-by-step setup (5 steps)
- Copy-paste examples
- Minimal explanations
- Get running fast

## How It Works

### Architecture Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     User Browser                             │
│                  http://localhost:8000                       │
└────────────────────┬────────────────────────────────────────┘
                     │ Auto-refresh every 5s
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                  FastAPI Server                              │
│                   (app/main.py)                              │
│                                                              │
│  ┌──────────────────────────────────────────────┐          │
│  │  /admin/poll endpoint (manual trigger)       │          │
│  │         ↓                                     │          │
│  │   poll_once()                                 │          │
│  │         ↓                                     │          │
│  │   fetch_state()  ← config.settings          │          │
│  └──────────┬───────────────────────────────────┘          │
└─────────────┼──────────────────────────────────────────────┘
              │
              ↓
     ┌────────┴─────────┐
     │  DEMO_MODE?      │
     └────────┬─────────┘
              │
       ┌──────┴───────┐
       │              │
    YES│             │NO
       ↓              ↓
┌──────────────┐  ┌────────────────────────────┐
│ Demo Feed    │  │  fetch_live_espn_state()  │
│ (JSON file)  │  │                            │
└──────────────┘  │  ┌──────────────────────┐ │
                  │  │ ESPN API             │ │
                  │  │ GET /summary         │ │
                  │  │ ?event={game_id}     │ │
                  │  └──────────────────────┘ │
                  │           ↓                │
                  │  Parse game data:          │
                  │  - Score                   │
                  │  - Quarter/Clock           │
                  │  - Status                  │
                  │  - Player stats            │
                  └────────────────────────────┘
                              ↓
                  ┌───────────────────────┐
                  │   GameState object    │
                  └───────────────────────┘
                              ↓
                  ┌───────────────────────┐
                  │  AI Commentary        │
                  │  (if state changed)   │
                  └───────────────────────┘
                              ↓
                  ┌───────────────────────┐
                  │  Update UI            │
                  └───────────────────────┘
```

### State Detection (Edge-Triggered)

The system only updates when game state **actually changes**:

1. **Fingerprint**: Hash of game state (score, quarter, clock, player stats)
2. **Compare**: New fingerprint vs last fingerprint
3. **Update**: Only trigger AI commentary if fingerprint changed

This prevents:
- Unnecessary API calls
- Duplicate commentary
- Wasted AI tokens

### Data Flow Example

```python
# User clicks "Poll Now"
POST /admin/poll

# Server fetches current state
state = await fetch_state()
  ↓
# If DEMO_MODE=0
state = await fetch_live_espn_state()
  ↓
# ESPN API call
GET https://site.api.espn.com/.../summary?event=401635594
  ↓
# Parse response
{
  "home_score": 17,
  "away_score": 14,
  "quarter": 3,
  "clock": "8:42",
  "status": "live",
  "mendoza_pass_yds": 214,
  "mendoza_td": 2,
  "mendoza_int": 1
}
  ↓
# Create GameState object
GameState(home_score=17, away_score=14, ...)
  ↓
# Compute fingerprint
fp = fingerprint(state)  # SHA256 hash
  ↓
# Compare with last fingerprint
if fp != last_fp:
    # State changed! Generate AI commentary
    commentary = await ai_live_commentary(state)
    ↓
    # Update UI
    STORE.commentary.insert(0, commentary)
```

## Environment Variables

### Demo Mode (Default)
```bash
DEMO_MODE=1
OPENAI_API_KEY=sk-...
```

### Live Mode
```bash
DEMO_MODE=0
ESPN_GAME_ID=401635594
HOME_TEAM=Miami
AWAY_TEAM=Indiana
TRACKED_PLAYER=Fernando Mendoza
OPENAI_API_KEY=sk-...
```

## ESPN API Details

### Endpoints Used

1. **Scoreboard** (for finding games)
   ```
   GET https://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard
   ```
   - Returns all current games
   - Used by `find_live_games.py`

2. **Game Summary** (for live data)
   ```
   GET https://site.api.espn.com/apis/site/v2/sports/football/college-football/summary?event={game_id}
   ```
   - Returns detailed game data
   - Used by `fetch_live_espn_state()`

### Data Extracted

From ESPN API response:
```json
{
  "header": {
    "competitions": [{
      "competitors": [
        {
          "homeAway": "home",
          "team": {"displayName": "Miami"},
          "score": 17
        },
        {
          "homeAway": "away",
          "team": {"displayName": "Indiana"},
          "score": 14
        }
      ],
      "status": {
        "type": {"name": "in"},
        "period": 3,
        "displayClock": "8:42"
      }
    }]
  },
  "boxscore": {
    "players": [{
      "statistics": [{
        "name": "passing",
        "athletes": [{
          "athlete": {"displayName": "Fernando Mendoza"},
          "stats": ["14", "23", "214", "9.3", "2", "1", "1-7", "78.4"]
        }]
      }]
    }]
  }
}
```

### Stats Array Format
```python
stats = [
  completions,  # 0
  attempts,     # 1
  yards,        # 2
  avg,          # 3
  td,           # 4
  int,          # 5
  sacks,        # 6
  qbr           # 7
]
```

## Testing

### 1. Find Games
```bash
python find_live_games.py
```

### 2. Test ESPN Integration
```bash
python test_espn_live.py 401635594
```

### 3. Run Full App
```bash
# Set environment
export DEMO_MODE=0
export ESPN_GAME_ID=401635594
export OPENAI_API_KEY=sk-...

# Start server
uvicorn app.main:app --reload
```

### 4. Access Dashboard
```
http://localhost:8000
```

## Backwards Compatibility

✅ **Fully backwards compatible!**

- Demo mode still works exactly as before
- Default settings unchanged (`DEMO_MODE=1`)
- No breaking changes to existing functionality
- Live mode is opt-in via environment variables

## Future Enhancements

Potential additions:
- [ ] Multiple player tracking
- [ ] Team stats (rushing, defense)
- [ ] Play-by-play feed
- [ ] Drive charts
- [ ] Historical game data
- [ ] WebSocket live updates
- [ ] Auto-detect close games
- [ ] Betting odds integration

## Troubleshooting

### Common Issues

1. **"No games found"**
   - Check it's football season
   - Verify internet connection
   - Try during game hours

2. **"Player stats not found"**
   - Check player name spelling
   - Verify player is in the game
   - Look at ESPN.com roster

3. **"Connection error"**
   - Verify game ID is correct
   - Check ESPN API status
   - Wait and retry (rate limits)

4. **"Module not found: httpx"**
   - Install dependencies: `pip install httpx`
   - See SETUP.md for detailed instructions

## Summary

**Before:** Demo mode only, pre-recorded events  
**After:** Live ESPN data + demo mode

**Key Benefits:**
- ✅ Real-time game tracking
- ✅ Live player stats
- ✅ Auto-updating dashboard
- ✅ Edge-triggered updates (efficient)
- ✅ No breaking changes
- ✅ Easy configuration

**Files Changed:** 3  
**Files Created:** 4  
**Lines Added:** ~350  
**Dependencies Added:** 0 (httpx already in pyproject.toml)
