# Setup Guide

## Environment Configuration

### Required Environment Variables

Create a `.env` file in the project root with these variables:

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `DEMO_MODE` | Use demo data (1) or live ESPN data (0) | No (default: 1) | `0` |
| `ESPN_GAME_ID` | ESPN game ID for live tracking | Yes (if DEMO_MODE=0) | `401635594` |
| `HOME_TEAM` | Home team name | No | `Miami` |
| `AWAY_TEAM` | Away team name | No | `Indiana` |
| `TRACKED_PLAYER` | Player to track for stats | No | `Fernando Mendoza` |
| `KICKOFF_ISO` | Game kickoff time (ISO format) | No | `2026-01-19T16:30:00-08:00` |
| `OPENAI_API_KEY` | OpenAI API key (OPTIONAL - not used) | No | `sk-...` |
| `OPENAI_MODEL` | OpenAI model (OPTIONAL - not used) | No (default: gpt-4o-mini) | `gpt-4o-mini` |

**Note:** OpenAI API key is NOT required! The app uses intelligent rule-based commentary.

### Example .env Files

#### Live Game Tracking
```bash
# Track live game from ESPN
DEMO_MODE=0
ESPN_GAME_ID=401635594
HOME_TEAM=Miami
AWAY_TEAM=Indiana
TRACKED_PLAYER=Fernando Mendoza
KICKOFF_ISO=2026-01-19T16:30:00-08:00
```

#### Demo Mode (Testing)
```bash
# Use pre-recorded demo data
DEMO_MODE=1
HOME_TEAM=Miami
AWAY_TEAM=Indiana
```

**No API keys needed!** The system generates commentary using intelligent rules.

## Finding Live Games

### Step 1: Run the game finder
```bash
python find_live_games.py
```

### Step 2: Copy the Game ID
The script will display all current games:

```
🔴 LIVE IND @ MIA
  Game ID: 401635594          <-- Copy this
  Indiana @ Miami
  Score: 14 - 17
  Status: 3rd Quarter
```

### Step 3: Update .env
```bash
ESPN_GAME_ID=401635594
```

## Installation Troubleshooting

### SSL Certificate Errors

If you see SSL errors when installing packages:

```bash
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org httpx fastapi uvicorn jinja2 python-dotenv pydantic
```

### Permission Errors

If you get permission errors:

1. **Using virtualenv (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install httpx fastapi uvicorn jinja2 python-dotenv pydantic
   ```

2. **Or fix permissions:**
   ```bash
   sudo chown -R $USER ~/.pyenv
   ```

### Dependencies Already Satisfied

If dependencies are in a different environment, create a fresh virtualenv:
```bash
python -m venv venv
source venv/bin/activate
pip install httpx fastapi uvicorn jinja2 python-dotenv pydantic
```

## Running the Application

### Start the server
```bash
uvicorn app.main:app --reload
```

### Access the dashboard
Open your browser to: http://localhost:8000

### Manual polling
If auto-polling doesn't work, use the admin endpoint:
```bash
curl -X POST http://localhost:8000/admin/poll
```

## How It Works

### Demo Mode
- Reads from `demo_data/demo_events.json`
- Steps through pre-recorded game states
- No external API calls needed
- Perfect for testing and development

### Live Mode
- Fetches data from ESPN API every poll
- Updates only when game state changes (edge-triggered)
- Tracks:
  - Score
  - Quarter and clock
  - Game status (pregame/live/final)
  - Player stats (passing yards, TDs, INTs)
- AI generates commentary on state changes

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main dashboard UI |
| `/api/state` | GET | Get current game state JSON |
| `/api/settings` | GET | Get current settings |
| `/admin/poll` | POST | Manually trigger a poll |
| `/admin/clear/{panel}` | POST | Clear a panel (commentary/mendoza/winprob/recap/all) |

## ESPN API Details

The app uses ESPN's public college football API:

- **Scoreboard:** `https://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard`
- **Game Details:** `https://site.api.espn.com/apis/site/v2/sports/football/college-football/summary?event={game_id}`

No API key required for ESPN data.

## Troubleshooting

### No games showing up
- Check that college football season is active
- Verify your internet connection
- Try running `find_live_games.py` to see available games

### Player stats not showing
- Verify the player name matches exactly (check ESPN roster)
- Player must be playing in the game
- Stats update after plays are recorded by ESPN

### Commentary not showing
- Make sure you've polled at least once (click "Poll Now")
- Check that game state is actually changing
- Commentary only updates on state changes (edge-triggered)

### Game state not updating
- Verify `ESPN_GAME_ID` is correct
- Check that the game is currently live
- ESPN updates can have 30-60 second delays
