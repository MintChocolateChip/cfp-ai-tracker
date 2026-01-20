# Event-Driven CFP Analysis Engine

This project demonstrates a deterministic, event-driven analysis system inspired by
hardware and embedded design principles. It tracks live college football games with intelligent rule-based commentary.

🎉 **No API keys required!** Uses smart rule-based analysis instead of expensive AI APIs.

## Key Ideas
- Finite state machine (PREGAME → LIVE → FINAL)
- Edge-triggered state transitions
- Explainable probability model
- Intelligent rule-based commentary (no API keys!)
- Real-time ESPN data integration
- Zero cost, instant feedback

## Quick Start

### 1. Install Dependencies

You may need to use `--trusted-host` flags if you encounter SSL certificate issues:

```bash
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org httpx fastapi uvicorn jinja2 python-dotenv pydantic
```

Or simply:
```bash
pip install httpx fastapi uvicorn jinja2 python-dotenv pydantic
```

### 2. Find a Live Game

Run the helper script to see current games and get the ESPN game ID:

```bash
python find_live_games.py
```

This will show all current college football games with their IDs, status, and scores like:

```
🔴 LIVE IND @ MIA
  Game ID: 401635594
  Indiana @ Miami
  Score: 14 - 17
  Status: 3rd Quarter
  Q3 - 8:42
```

### 3. Configure Environment

Create a `.env` file in the project root:

**For Live Games:**
```bash
DEMO_MODE=0
ESPN_GAME_ID=401635594
HOME_TEAM=Miami
AWAY_TEAM=Indiana
TRACKED_PLAYER=Fernando Mendoza
```

**For Demo Mode (no live data, just testing):**
```bash
DEMO_MODE=1
```

**Note:** OpenAI API key is NOT required! The app uses intelligent rule-based commentary that works without any API keys.

### 4. Run the Server

```bash
uvicorn app.main:app --reload
```

Then open http://localhost:8000 in your browser.

### 5. Start Tracking

The page will auto-poll every few seconds, or manually:
- Click "Poll Game" button in the UI
- `POST /admin/poll` - Fetch latest game state
- `GET /api/state` - Get current state JSON

## How It Works

### Live Mode (DEMO_MODE=0)
- Fetches real-time data from ESPN's API
- Tracks game score, quarter, clock, and player stats
- Updates only when game state changes (edge-triggered)
- AI generates commentary on significant events

### Demo Mode (DEMO_MODE=1)
- Steps through pre-recorded game events
- Perfect for testing and development
- No API rate limits or dependencies

## Architecture

The intelligence lives in the system design:
- **Deterministic**: Same input → same output
- **Edge-triggered**: Updates only on state changes
- **Explainable**: Win probability uses simple heuristics
- **Efficient**: No unnecessary polling or API calls

Built for fun by a hardware-focused engineer.
