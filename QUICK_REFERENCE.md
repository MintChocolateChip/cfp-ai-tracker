# Quick Reference Card

## ⚡ Super Quick Start

```bash
# 1. Install
pip install httpx fastapi uvicorn jinja2 python-dotenv pydantic

# 2. Find game
python find_live_games.py

# 3. Configure (NO API KEY NEEDED!)
echo "DEMO_MODE=0" > .env
echo "ESPN_GAME_ID=401635594" >> .env

# 4. Run
uvicorn app.main:app --reload

# 5. Open browser
# http://localhost:8000
```

## 🎯 Key Commands

| Command | Purpose |
|---------|---------|
| `python find_live_games.py` | Find live games + get ESPN IDs |
| `python test_espn_live.py <ID>` | Test ESPN API connection |
| `python test_commentary.py` | Demo the commentary system |
| `uvicorn app.main:app --reload` | Start the server |

## ⚙️ Environment Variables (.env)

```bash
# Required for live mode
DEMO_MODE=0
ESPN_GAME_ID=401635594

# Optional
HOME_TEAM=Miami
AWAY_TEAM=Indiana
TRACKED_PLAYER=Fernando Mendoza
KICKOFF_ISO=2026-01-19T16:30:00-08:00
```

**Note:** `OPENAI_API_KEY` is NOT required!

## 🌐 Endpoints

| URL | Method | Purpose |
|-----|--------|---------|
| http://localhost:8000 | GET | Main dashboard |
| http://localhost:8000/api/state | GET | Current state JSON |
| http://localhost:8000/admin/poll | POST | Trigger update |
| http://localhost:8000/admin/clear/all | POST | Clear all panels |

## 📊 What Gets Tracked

✅ Live scores  
✅ Quarter + clock  
✅ Game status  
✅ Player passing stats (yards, TDs, INTs)  
✅ Intelligent commentary  
✅ Win probability  
✅ Postgame recap  

## 💬 Commentary Examples

**Close Game:**
> "Miami leads 24-21 in crunch time. Indiana needs a stop here."

**Player Stats:**
> "287 passing yards, 3 TD, 1 INT. Solid production through the air. More positives than negatives."

**Win Probability:**
> "Late one-score game - single drive can flip outcome"

**Postgame:**
> "FINAL: Miami defeats Indiana 27-24. This nail-biter came down to the final possessions."

## 🔄 Mode Switching

**Demo Mode** (pre-recorded data):
```bash
DEMO_MODE=1
```

**Live Mode** (ESPN API):
```bash
DEMO_MODE=0
ESPN_GAME_ID=401635594
```

## 🐛 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| Dependencies won't install | Use virtualenv: `python -m venv venv` |
| No games found | Check if it's football season + game hours |
| Player stats missing | Verify player name matches ESPN exactly |
| Commentary not showing | Click "Poll Now" to trigger update |

## 📚 Documentation

- **Quick Start**: [QUICKSTART.md](QUICKSTART.md) - 5 min setup
- **No API Key**: [NO_API_KEY_NEEDED.md](NO_API_KEY_NEEDED.md) - Commentary details
- **Full Setup**: [SETUP.md](SETUP.md) - Comprehensive guide
- **Changes**: [CHANGES.md](CHANGES.md) - Technical details

## 🎓 How It Works

```
Browser → FastAPI → ESPN API → Parse Data → Generate Commentary → Update UI
                                              ↑
                                    Rule-Based (No AI API!)
```

## ✅ No API Keys Needed!

The commentary system uses **intelligent rules** that analyze:
- Score differential
- Game quarter/time
- Momentum shifts
- Player efficiency
- Ball security

**Zero cost. Instant. Reliable.**

## 🎉 That's It!

You're ready to track live college football games with intelligent commentary!

```bash
python find_live_games.py  # Start here!
```
