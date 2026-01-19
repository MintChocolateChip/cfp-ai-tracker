from pydantic import BaseModel
import os

class Settings(BaseModel):
    demo_mode: bool = os.getenv("DEMO_MODE", "1") == "1"
    kickoff_iso: str = os.getenv("KICKOFF_ISO", "2026-01-19T16:30:00-08:00")
    home_team: str = os.getenv("HOME_TEAM", "Miami")
    away_team: str = os.getenv("AWAY_TEAM", "Indiana")
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY") or None
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

settings = Settings()
