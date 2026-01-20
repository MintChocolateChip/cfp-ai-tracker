async def ai_live_commentary(event: dict) -> str:
    s = event.get("state", {})
    hs, ays = s.get("home_score", 0), s.get("away_score", 0)
    q = s.get("quarter")
    clock = s.get("clock", "")
    status = s.get("status")
    home = s.get("home_team", "Home")
    away = s.get("away_team", "Away")
    
    # Pregame
    if status == "pregame":
        return f"Pregame: {away} at {home}. Teams warming up, kickoff approaching."
    
    # Game is live
    margin = abs(hs - ays)
    leader = home if hs > ays else away
    trailer = away if hs > ays else home
    
    # Tied game
    if hs == ays:
        if q == 4:
            return f"Tied {hs}-{ays} in the 4th quarter! Every possession crucial."
        elif q == 3:
            return f"All square at {hs}-{ays}. Third quarter - game still wide open."
        else:
            return f"Score tied {hs}-{hs}. Both teams trading blows early."
    
    # One-score game (1-8 points)
    if margin <= 8:
        if q == 4:
            return f"{leader} leads {hs}-{ays} in crunch time. {trailer} needs a stop here."
        elif q == 3:
            return f"{leader} up {hs}-{ays}. One-score game heading into the 4th."
        else:
            return f"{leader} holds slim {hs}-{ays} advantage. Still anyone's game."
    
    # Two-score game (9-16 points)
    elif margin <= 16:
        if q == 4:
            return f"{leader} leads {hs}-{ays} late. {trailer} needs scores on consecutive drives."
        else:
            return f"{leader} building momentum, up {hs}-{ays}. {trailer} needs an answer."
    
    # Blowout (17+ points)
    else:
        if q >= 3:
            return f"{leader} in command {hs}-{ays}. Dominant performance unfolding."
        else:
            return f"{leader} jumps ahead {hs}-{ays}. Early statement being made."

async def ai_mendoza_watch(state: dict) -> str:
    m = state.get("mendoza", {})
    yds = m.get("pass_yds")
    tds = m.get("td", 0)
    ints = m.get("int", 0)
    
    if yds is None:
        return "Player stats not yet available. Check back after first quarter."
    
    # Build detailed analysis based on performance
    stat_line = f"{yds} passing yards, {tds} TD, {ints} INT"
    
    # Efficiency analysis
    if yds > 300:
        efficiency = "Outstanding passing day"
    elif yds > 200:
        efficiency = "Solid production through the air"
    elif yds > 100:
        efficiency = "Steady performance"
    else:
        efficiency = "Limited passing output"
    
    # TD/INT ratio analysis
    if tds > 0 and ints == 0:
        decision = "Clean decision-making, protecting the football"
    elif tds > ints:
        decision = "More positives than negatives"
    elif tds == ints:
        decision = "Mixed results in the turnover battle"
    else:
        decision = "Struggling with ball security"
    
    return f"{stat_line}. {efficiency}. {decision}."

async def ai_winprob_explain(state: dict, wp: float) -> str:
    q = state.get("quarter")
    status = state.get("status")
    hs = state.get("home_score", 0)
    ays = state.get("away_score", 0)
    margin = abs(hs - ays)
    
    if status == "pregame":
        return "Even odds before kickoff"
    
    if status == "final":
        return "Game complete"
    
    # Build context-aware explanation
    if q == 1:
        return "Early - score margin has less predictive weight"
    elif q == 2:
        if margin <= 7:
            return "Close at halftime - game very much in flux"
        else:
            return "Lead established but plenty of time remains"
    elif q == 3:
        if margin <= 3:
            return "One possession game in 3rd - critical juncture"
        else:
            return "Margin grows more significant as time dwindles"
    elif q == 4:
        if margin <= 7:
            return "Late one-score game - single drive can flip outcome"
        elif margin <= 14:
            return "Two-score lead late - needs multiple possessions to overcome"
        else:
            return "Commanding lead with clock becoming a factor"
    
    return "Win probability based on score margin and time remaining"

async def ai_postgame_recap(final_state: dict, winprob_history: list[str], mendoza_notes: list[str]) -> str:
    home = final_state["home_team"]
    away = final_state["away_team"]
    hs = final_state["home_score"]
    ays = final_state["away_score"]
    winner = home if hs > ays else away
    loser = away if winner == home else home
    winning_score = max(hs, ays)
    losing_score = min(hs, ays)
    margin = winning_score - losing_score
    
    # Game characterization
    if margin <= 3:
        game_type = "nail-biter"
        outcome_desc = "came down to the final possessions"
    elif margin <= 7:
        game_type = "close contest"
        outcome_desc = "was decided by a single score"
    elif margin <= 14:
        game_type = "competitive matchup"
        outcome_desc = "saw the winner pull away in the second half"
    else:
        game_type = "one-sided affair"
        outcome_desc = "was never really in doubt"
    
    # Build recap
    recap = f"FINAL: {winner} defeats {loser} {winning_score}-{losing_score}. "
    recap += f"This {game_type} {outcome_desc}. "
    
    # Add player note if available
    if mendoza_notes and mendoza_notes[0]:
        recap += f"Key stat: {mendoza_notes[0]} "
    
    recap += f"{winner} advances with the victory."
    
    return recap
