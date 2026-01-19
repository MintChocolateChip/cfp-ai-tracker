from __future__ import annotations

from datetime import datetime, timezone

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.data_sources import fetch_state, demo_get_index, demo_set_index
from app.game_logic import (
    fingerprint,
    kickoff_countdown,
    compute_win_prob_simple,
    game_phase,
)
from app.store import STORE
from app.ai_engine import (
    ai_live_commentary,
    ai_mendoza_watch,
    ai_winprob_explain,
    ai_postgame_recap,
)
from app.persist import load_state, save_state
from app.assets import team_logo_url, player_image_url

PLAYER_NAME = "Fernando Mendoza"

app = FastAPI(title="Event-Driven CFP Analysis Engine")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def _norm(s: str) -> str:
    return " ".join((s or "").strip().lower().split())

def _dedupe_insert(buf: list[str], text: str, max_items: int = 50) -> None:
    t = (text or "").strip()
    if not t:
        return
    nt = _norm(t)
    for existing in buf[:10]:
        if _norm(existing) == nt:
            return
    buf.insert(0, t)
    del buf[max_items:]


def _asset_payload(state: dict | None) -> dict:
    away = (state or {}).get("away_team", settings.away_team)
    home = (state or {}).get("home_team", settings.home_team)
    return {
        "away_logo": team_logo_url(away),
        "home_logo": team_logo_url(home),
        "player_name": PLAYER_NAME,
        "player_img": player_image_url(PLAYER_NAME),
    }

def _payload() -> dict:
    assets = _asset_payload(STORE.last_state)
    return {
        "state": STORE.last_state,
        "commentary": STORE.commentary[:20],
        "mendoza_notes": STORE.mendoza_notes[:20],
        "winprob_home": STORE.winprob_home,
        "winprob_history": STORE.winprob_history[:20],
        "postgame_recap": STORE.postgame_recap,
        "meta": {
            "poll_count": STORE.poll_count,
            "last_update_iso": STORE.last_update_iso,
            "demo_mode": settings.demo_mode,
            "demo_idx": demo_get_index() if settings.demo_mode else None,
        },
        **assets,
    }

def _persist() -> None:
    # Persist ONLY what we need to resume demo position.
    save_state({
        "meta": {
            "demo_mode": settings.demo_mode,
            "demo_idx": demo_get_index() if settings.demo_mode else None,
        }
    })

def _hydrate_from_disk() -> None:
    saved = load_state()
    if not saved:
        return
    meta = (saved.get("meta") or {})
    if settings.demo_mode and meta.get("demo_idx") is not None:
        demo_set_index(meta.get("demo_idx"))

    # Panels regenerate fresh after restart:
    STORE.last_fingerprint = None
    STORE.commentary.clear()
    STORE.mendoza_notes.clear()
    STORE.winprob_history.clear()
    STORE.winprob_home = None
    STORE.postgame_recap = None
    STORE.last_state = None
    STORE.poll_count = 0
    STORE.last_update_iso = None

_hydrate_from_disk()


async def poll_once() -> None:
    state_obj = await fetch_state()
    state = state_obj.to_dict()
    state["phase"] = game_phase(state_obj)
    STORE.last_state = state

    fp = fingerprint(state_obj)
    STORE.poll_count += 1
    STORE.last_update_iso = _now_iso()

    if STORE.last_fingerprint == fp:
        _persist()
        return
    STORE.last_fingerprint = fp

    _dedupe_insert(STORE.commentary, await ai_live_commentary({"state": state}))
    _dedupe_insert(STORE.mendoza_notes, await ai_mendoza_watch(state))

    wp = compute_win_prob_simple(state_obj)
    STORE.winprob_home = wp
    expl = await ai_winprob_explain(state, wp)
    leader = state["home_team"] if wp >= 0.5 else state["away_team"]
    pct = int(wp * 100) if wp >= 0.5 else int((1 - wp) * 100)
    _dedupe_insert(STORE.winprob_history, f"{leader} {pct}% — {expl}")

    if state["status"] == "final" and STORE.postgame_recap is None:
        STORE.postgame_recap = await ai_postgame_recap(
            state,
            STORE.winprob_history[:10],
            STORE.mendoza_notes[:10],
        )

    _persist()


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    if STORE.last_state is None:
        STORE.last_state = {
            "home_team": settings.home_team,
            "away_team": settings.away_team,
            "home_score": 0,
            "away_score": 0,
            "status": "pregame",
            "quarter": None,
            "clock": None,
            "mendoza": {"pass_yds": None, "td": None, "int": None},
            "phase": "PREGAME",
        }

    assets = _asset_payload(STORE.last_state)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "kickoff": settings.kickoff_iso,
            "countdown": kickoff_countdown(settings.kickoff_iso),
            "state": STORE.last_state,
            "commentary": STORE.commentary[:20],
            "mendoza_notes": STORE.mendoza_notes[:20],
            "winprob_history": STORE.winprob_history[:20],
            "winprob_home": STORE.winprob_home,
            "postgame_recap": STORE.postgame_recap,
            "meta": {"poll_count": STORE.poll_count, "last_update_iso": STORE.last_update_iso},
            **assets,
        },
    )


@app.post("/admin/poll")
async def admin_poll():
    await poll_once()
    return JSONResponse({"ok": True, **_payload()})


@app.get("/api/state")
async def api_state():
    return JSONResponse(_payload())


@app.post("/admin/clear/{panel}")
async def clear_panel(panel: str):
    panel = panel.lower()
    if panel == "commentary":
        STORE.commentary.clear()
    elif panel == "mendoza":
        STORE.mendoza_notes.clear()
    elif panel == "winprob":
        STORE.winprob_history.clear()
        STORE.winprob_home = None
    elif panel == "recap":
        STORE.postgame_recap = None
    elif panel == "all":
        STORE.commentary.clear()
        STORE.mendoza_notes.clear()
        STORE.winprob_history.clear()
        STORE.winprob_home = None
        STORE.postgame_recap = None
    else:
        raise HTTPException(status_code=400, detail="panel must be one of: commentary, mendoza, winprob, recap, all")

    STORE.last_update_iso = _now_iso()
    _persist()
    return JSONResponse({"ok": True, **_payload()})


@app.get("/api/settings")
async def api_settings():
    return JSONResponse({"demo_mode": settings.demo_mode})
