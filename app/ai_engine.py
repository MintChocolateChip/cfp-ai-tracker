async def ai_live_commentary(event: dict) -> str:
    s = event.get("state", {})
    hs, ays = s.get("home_score", 0), s.get("away_score", 0)
    if s.get("status") == "pregame":
        return "Pregame: teams are finalizing lineups; kickoff approaching."
    if hs > ays:
        return f"{s.get('home_team')} leads {hs}-{ays}. Momentum favors the current leader."
    if ays > hs:
        return f"{s.get('away_team')} leads {ays}-{hs}. Recent scoring swing shifted control."
    return "Score tied — next possession is a leverage point."

async def ai_mendoza_watch(state: dict) -> str:
    m = state.get("mendoza", {})
    if m.get("pass_yds") is None:
        return "Mendoza Watch: no stats yet."
    return (
        f"Mendoza Watch: {m['pass_yds']} yds, "
        f"{m['td']} TD, {m['int']} INT — decision-making remains the key variable."
    )

async def ai_winprob_explain(state: dict, wp: float) -> str:
    if state.get("status") == "pregame":
        return "Baseline estimate before kickoff."
    if state.get("quarter") in (3,4):
        return "Late-game margin carries more weight with fewer remaining possessions."
    return "Win probability tracks score margin and time remaining."

async def ai_postgame_recap(final_state: dict, winprob_history: list[str], mendoza_notes: list[str]) -> str:
    home = final_state["home_team"]
    away = final_state["away_team"]
    hs = final_state["home_score"]
    ays = final_state["away_score"]
    winner = home if hs > ays else away
    loser = away if winner == home else home
    return (
        f"Final: {winner} defeats {loser} {max(hs,ays)}-{min(hs,ays)}. "
        "The outcome was decided by late-game execution and possession efficiency. "
        f"{mendoza_notes[:1][0] if mendoza_notes else ''}"
    )
