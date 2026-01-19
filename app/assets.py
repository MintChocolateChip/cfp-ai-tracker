from __future__ import annotations
import os

# Defaults (Wikimedia CDN). You can override with env vars later.
DEFAULT_TEAM_LOGOS = {
    "indiana": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/Indiana_Hoosiers_logo.svg/330px-Indiana_Hoosiers_logo.svg.png",
    "miami":   "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e9/Miami_Hurricanes_logo.svg/500px-Miami_Hurricanes_logo.svg.png",
}

DEFAULT_PLAYER_IMAGES = {
    # Fernando Mendoza headshot (Wikimedia CDN)
    "fernando mendoza": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7a/2026-0117_Fernando_Mendoza.jpeg/250px-2026-0117_Fernando_Mendoza.jpeg",
}

def _k(s: str) -> str:
    return (s or "").strip().lower()

def team_logo_url(team_name: str) -> str | None:
    # Optional overrides:
    #   TEAM_LOGO_INDIANA="https://..."
    #   TEAM_LOGO_MIAMI="https://..."
    key = _k(team_name)
    env_key = f"TEAM_LOGO_{key.replace(' ', '_').upper()}"
    if os.getenv(env_key):
        return os.getenv(env_key)
    return DEFAULT_TEAM_LOGOS.get(key)

def player_image_url(player_name: str) -> str | None:
    # Optional override:
    #   PLAYER_IMG_FERNANDO_MENDOZA="https://..."
    key = _k(player_name)
    env_key = f"PLAYER_IMG_{key.replace(' ', '_').upper()}"
    if os.getenv(env_key):
        return os.getenv(env_key)
    return DEFAULT_PLAYER_IMAGES.get(key)
