"""Static NFL team metadata: names, colors, divisions, conferences.

`primary`/`secondary` are each franchise's true brand colors. `map_color` is
a viz-tuned choice used for the map markers: because so many teams share dark
navy/red primaries, we lean on each club's brighter signature shade so all 32
teams stay visually distinct on a light basemap. Abbreviations follow the
nflverse convention.
"""

# abbr -> metadata
TEAMS = {
    "ARI": {"name": "Arizona Cardinals",     "conf": "NFC", "div": "West",  "primary": "#97233F", "secondary": "#000000", "map_color": "#A4133C"},
    "ATL": {"name": "Atlanta Falcons",       "conf": "NFC", "div": "South", "primary": "#A71930", "secondary": "#000000", "map_color": "#E8262A"},
    "BAL": {"name": "Baltimore Ravens",      "conf": "AFC", "div": "North", "primary": "#241773", "secondary": "#9E7C0C", "map_color": "#6A2D91"},
    "BUF": {"name": "Buffalo Bills",         "conf": "AFC", "div": "East",  "primary": "#00338D", "secondary": "#C60C30", "map_color": "#0057B8"},
    "CAR": {"name": "Carolina Panthers",     "conf": "NFC", "div": "South", "primary": "#0085CA", "secondary": "#101820", "map_color": "#00A3E0"},
    "CHI": {"name": "Chicago Bears",         "conf": "NFC", "div": "North", "primary": "#0B162A", "secondary": "#C83803", "map_color": "#E35205"},
    "CIN": {"name": "Cincinnati Bengals",    "conf": "AFC", "div": "North", "primary": "#FB4F14", "secondary": "#000000", "map_color": "#FB4F14"},
    "CLE": {"name": "Cleveland Browns",      "conf": "AFC", "div": "North", "primary": "#311D00", "secondary": "#FF3C00", "map_color": "#6B3A1E"},
    "DAL": {"name": "Dallas Cowboys",        "conf": "NFC", "div": "East",  "primary": "#003594", "secondary": "#869397", "map_color": "#0B2D6E"},
    "DEN": {"name": "Denver Broncos",        "conf": "AFC", "div": "West",  "primary": "#FB4F14", "secondary": "#002244", "map_color": "#FF7418"},
    "DET": {"name": "Detroit Lions",         "conf": "NFC", "div": "North", "primary": "#0076B6", "secondary": "#B0B7BC", "map_color": "#1E90C4"},
    "GB":  {"name": "Green Bay Packers",     "conf": "NFC", "div": "North", "primary": "#203731", "secondary": "#FFB612", "map_color": "#2FA84F"},
    "HOU": {"name": "Houston Texans",        "conf": "AFC", "div": "South", "primary": "#03202F", "secondary": "#A71930", "map_color": "#B31942"},
    "IND": {"name": "Indianapolis Colts",    "conf": "AFC", "div": "South", "primary": "#002C5F", "secondary": "#A2AAAD", "map_color": "#1D63B3"},
    "JAX": {"name": "Jacksonville Jaguars",  "conf": "AFC", "div": "South", "primary": "#006778", "secondary": "#9F792C", "map_color": "#158A98"},
    "KC":  {"name": "Kansas City Chiefs",    "conf": "AFC", "div": "West",  "primary": "#E31837", "secondary": "#FFB81C", "map_color": "#CE1126"},
    "LV":  {"name": "Las Vegas Raiders",     "conf": "AFC", "div": "West",  "primary": "#000000", "secondary": "#A5ACAF", "map_color": "#111111"},
    "LAC": {"name": "Los Angeles Chargers",  "conf": "AFC", "div": "West",  "primary": "#0080C6", "secondary": "#FFC20E", "map_color": "#5FC0F0"},
    "LAR": {"name": "Los Angeles Rams",      "conf": "NFC", "div": "West",  "primary": "#003594", "secondary": "#FFA300", "map_color": "#274FC7"},
    "MIA": {"name": "Miami Dolphins",        "conf": "AFC", "div": "East",  "primary": "#008E97", "secondary": "#FC4C02", "map_color": "#00B2A9"},
    "MIN": {"name": "Minnesota Vikings",     "conf": "NFC", "div": "North", "primary": "#4F2683", "secondary": "#FFC62F", "map_color": "#7A42C0"},
    "NE":  {"name": "New England Patriots",  "conf": "AFC", "div": "East",  "primary": "#002244", "secondary": "#C60C30", "map_color": "#9CA3A8"},
    "NO":  {"name": "New Orleans Saints",    "conf": "NFC", "div": "South", "primary": "#D3BC8D", "secondary": "#101820", "map_color": "#C9AE6C"},
    "NYG": {"name": "New York Giants",       "conf": "NFC", "div": "East",  "primary": "#0B2265", "secondary": "#A71930", "map_color": "#1B4CA0"},
    "NYJ": {"name": "New York Jets",         "conf": "AFC", "div": "East",  "primary": "#125740", "secondary": "#000000", "map_color": "#046A38"},
    "PHI": {"name": "Philadelphia Eagles",   "conf": "NFC", "div": "East",  "primary": "#004C54", "secondary": "#A5ACAF", "map_color": "#006B5B"},
    "PIT": {"name": "Pittsburgh Steelers",   "conf": "AFC", "div": "North", "primary": "#FFB612", "secondary": "#101820", "map_color": "#FFB612"},
    "SEA": {"name": "Seattle Seahawks",      "conf": "NFC", "div": "West",  "primary": "#002244", "secondary": "#69BE28", "map_color": "#69BE28"},
    "SF":  {"name": "San Francisco 49ers",   "conf": "NFC", "div": "West",  "primary": "#AA0000", "secondary": "#B3995D", "map_color": "#AA0000"},
    "TB":  {"name": "Tampa Bay Buccaneers",  "conf": "NFC", "div": "South", "primary": "#D50A0A", "secondary": "#34302B", "map_color": "#D50A0A"},
    "TEN": {"name": "Tennessee Titans",      "conf": "AFC", "div": "South", "primary": "#0C2340", "secondary": "#4B92DB", "map_color": "#4B92DB"},
    "WAS": {"name": "Washington Commanders", "conf": "NFC", "div": "East",  "primary": "#5A1414", "secondary": "#FFB612", "map_color": "#7A2E2E"},
}

# Historical / alternate abbreviations mapped onto the current franchise.
ALIASES = {
    "OAK": "LV", "SD": "LAC", "STL": "LAR", "LA": "LAR",
    "AZ": "ARI", "WSH": "WAS", "ARZ": "ARI", "BLT": "BAL", "CLV": "CLE",
    "HST": "HOU", "JAC": "JAX", "SL": "LAR", "GNB": "GB",
    "KAN": "KC", "NWE": "NE", "NOR": "NO", "SFO": "SF", "TAM": "TB",
}


def canon(abbr: str) -> str:
    """Normalise any team abbreviation onto the current franchise code."""
    if not abbr:
        return ""
    a = abbr.strip().upper()
    return ALIASES.get(a, a)
