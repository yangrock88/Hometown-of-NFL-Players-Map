"""Central configuration for the data pipeline.

Everything that might change season-to-season lives here so refreshing the
map for a new year is a one-line edit.
"""
import os

SEASON = 2025  # bump this each season; the pipeline pulls this year's feeds.

# --- Paths -----------------------------------------------------------------
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")
CACHE_DIR = os.path.join(DATA_DIR, "cache")
ASSETS_DIR = os.path.join(ROOT, "assets")

# Output the map consumes. data.js works from file:// AND GitHub Pages.
OUT_DATA_JS = os.path.join(ASSETS_DIR, "data.js")
OUT_JSON = os.path.join(DATA_DIR, "players.json")

# --- nflverse release feeds -------------------------------------------------
NFLVERSE = "https://github.com/nflverse/nflverse-data/releases/download"
URL_PLAYERS = f"{NFLVERSE}/players/players.csv"
URL_ROSTERS = f"{NFLVERSE}/weekly_rosters/roster_weekly_{SEASON}.csv"
URL_DEPTH = f"{NFLVERSE}/depth_charts/depth_charts_{SEASON}.csv"
URL_CONTRACTS = f"{NFLVERSE}/contracts/historical_contracts.csv.gz"

# --- ESPN hidden athlete API (birthplace, jersey, etc.) ---------------------
ESPN_ATHLETE = ("https://sports.core.api.espn.com/v2/sports/football/"
                "leagues/nfl/athletes/{espn_id}")
ESPN_PROFILE = "https://www.espn.com/nfl/player/_/id/{espn_id}"

# --- Offline geocoding source (city, state -> lat/lng) ----------------------
US_CITIES_CSV = ("https://raw.githubusercontent.com/kelvins/"
                 "US-Cities-Database/main/csv/us_cities.csv")
NOMINATIM = "https://nominatim.openstreetmap.org/search"

USER_AGENT = "hometown-nfl-map/1.0 (Rocky Yang; personal portfolio project)"

# Roster statuses we treat as "currently on the roster".
ACTIVE_STATUSES = {"ACT", "RES", "PUP", "NON", "EXE", "DEV", "RSN"}

# How many lookups to run in parallel.
ESPN_WORKERS = 10
OTC_WORKERS = 6  # OverTheCap current-contract scrapes
