"""
config.py — Auth & app-wide constants.
Never commit this file with real credentials.
"""

import os

# ── Application ──────────────────────────────────────────────
APP_TITLE       = "TAM — EIKONA Dashboard"
APP_ICON        = "📡"
DB_PATH         = os.path.join(os.path.dirname(__file__), "tv_data.db")
DATA_DIR        = os.path.join(os.path.dirname(__file__), "data")
SHOWS_CSV       = os.path.join(DATA_DIR, "private_shows.csv")
CHANNELS_CSV    = os.path.join(DATA_DIR, "private_channels.csv")

# ── Roles ─────────────────────────────────────────────────────
ROLE_ADMIN   = "admin"
ROLE_CLIENT  = "client"
ROLE_PARTNER = "partner"

# ── Cookie / session (change before first deploy) ─────────────
COOKIE_NAME    = "eikona_auth_cookie"
COOKIE_KEY     = "eikona_super_secret_key_change_me_2024"   # ← CHANGE THIS
COOKIE_EXPIRY  = 1   # days

# ── streamlit-authenticator credentials structure ─────────────
FALLBACK_CREDENTIALS = {
    "usernames": {
        "admin": {
            "name": "Admin User",
            "password": "$2b$12$LQv3c1yqBwEHFj4eE3Fk5.vQH5k8TJz0ZTkQfRpXt9nV5g1O1hJry",
            "role": ROLE_ADMIN,
        },
        "client1": {
            "name": "Client Viewer",
            "password": "$2b$12$KlW9K8lP2mS3vU7xA6bQ4.dN0j2T3aP1RdF5yZsWt6m8Lq0G0kKxi",
            "role": ROLE_CLIENT,
        },
        "partner1": {
            "name": "Partner Access",
            "password": "$2b$12$HnX2m0pQ4kR6wT8yB5cL1.eO3i5W7bN2ScH4zYuVs9n0Mp1K0jJwu",
            "role": ROLE_PARTNER,
        },
    }
}

# ── Role-based access rules ────────────────────────────────────
ROLE_ACCESS = {
    ROLE_ADMIN:   ["analytics", "print", "online", "tv", "social", "admin"],
    ROLE_CLIENT:  ["analytics", "print", "online", "tv", "social"],
    ROLE_PARTNER: ["analytics", "print", "online", "tv", "social"],
}