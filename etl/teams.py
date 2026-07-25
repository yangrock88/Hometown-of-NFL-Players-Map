"""Static NFL team metadata: names, colors, divisions, conferences.

Colors follow each franchise's official primary/secondary palette. Team
abbreviations match the nflverse convention used across roster, depth chart
and contract feeds.
"""

# abbr -> metadata
TEAMS = {
    "ARI": {"name": "Arizona Cardinals",     "conf": "NFC", "div": "West",  "primary": "#97233F", "secondary": "#000000"},
    "ATL": {"name": "Atlanta Falcons",       "conf": "NFC", "div": "South", "primary": "#A71930", "secondary": "#000000"},
    "BAL": {"name": "Baltimore Ravens",      "conf": "AFC", "div": "North", "primary": "#241773", "secondary": "#9E7C0C"},
    "BUF": {"name": "Buffalo Bills",         "conf": "AFC", "div": "East",  "primary": "#00338D", "secondary": "#C60C30"},
    "CAR": {"name": "Carolina Panthers",     "conf": "NFC", "div": "South", "primary": "#0085CA", "secondary": "#101820"},
    "CHI": {"name": "Chicago Bears",         "conf": "NFC", "div": "North", "primary": "#0B162A", "secondary": "#C83803"},
    "CIN": {"name": "Cincinnati Bengals",    "conf": "AFC", "div": "North", "primary": "#FB4F14", "secondary": "#000000"},
    "CLE": {"name": "Cleveland Browns",      "conf": "AFC", "div": "North", "primary": "#311D00", "secondary": "#FF3C00"},
    "DAL": {"name": "Dallas Cowboys",        "conf": "NFC", "div": "East",  "primary": "#003594", "secondary": "#869397"},
    "DEN": {"name": "Denver Broncos",        "conf": "AFC", "div": "West",  "primary": "#FB4F14", "secondary": "#002244"},
    "DET": {"name": "Detroit Lions",         "conf": "NFC", "div": "North", "primary": "#0076B6", "secondary": "#B0B7BC"},
    "GB":  {"name": "Green Bay Packers",     "conf": "NFC", "div": "North", "primary": "#203731", "secondary": "#FFB612"},
    "HOU": {"name": "Houston Texans",        "conf": "AFC", "div": "South", "primary": "#03202F", "secondary": "#A71930"},
    "IND": {"name": "Indianapolis Colts",    "conf": "AFC", "div": "South", "primary": "#002C5F", "secondary": "#A2AAAD"},
    "JAX": {"name": "Jacksonville Jaguars",  "conf": "AFC", "div": "South", "primary": "#006778", "secondary": "#9F792C"},
    "KC":  {"name": "Kansas City Chiefs",    "conf": "AFC", "div": "West",  "primary": "#E31837", "secondary": "#FFB81C"},
    "LV":  {"name": "Las Vegas Raiders",     "conf": "AFC", "div": "West",  "primary": "#000000", "secondary": "#A5ACAF"},
    "LAC": {"name": "Los Angeles Chargers",  "conf": "AFC", "div": "West",  "primary": "#0080C6", "secondary": "#FFC20E"},
    "LAR": {"name": "Los Angeles Rams",      "conf": "NFC", "div": "West",  "primary": "#003594", "secondary": "#FFA300"},
    "MIA": {"name": "Miami Dolphins",        "conf": "AFC", "div": "East",  "primary": "#008E97", "secondary": "#FC4C02"},
    "MIN": {"name": "Minnesota Vikings",     "conf": "NFC", "div": "North", "primary": "#4F2683", "secondary": "#FFC62F"},
    "NE":  {"name": "New England Patriots",  "conf": "AFC", "div": "East",  "primary": "#002244", "secondary": "#C60C30"},
    "NO":  {"name": "New Orleans Saints",    "conf": "NFC", "div": "South", "primary": "#D3BC8D", "secondary": "#101820"},
    "NYG": {"name": "New York Giants",       "conf": "NFC", "div": "East",  "primary": "#0B2265", "secondary": "#A71930"},
    "NYJ": {"name": "New York Jets",         "conf": "AFC", "div": "East",  "primary": "#125740", "secondary": "#000000"},
    "PHI": {"name": "Philadelphia Eagles",   "conf": "NFC", "div": "East",  "primary": "#004C54", "secondary": "#A5ACAF"},
    "PIT": {"name": "Pittsburgh Steelers",   "conf": "AFC", "div": "North", "primary": "#FFB612", "secondary": "#101820"},
    "SEA": {"name": "Seattle Seahawks",      "conf": "NFC", "div": "West",  "primary": "#002244", "secondary": "#69BE28"},
    "SF":  {"name": "San Francisco 49ers",   "conf": "NFC", "div": "West",  "primary": "#AA0000", "secondary": "#B3995D"},
    "TB":  {"name": "Tampa Bay Buccaneers",  "conf": "NFC", "div": "South", "primary": "#D50A0A", "secondary": "#34302B"},
    "TEN": {"name": "Tennessee Titans",      "conf": "AFC", "div": "South", "primary": "#0C2340", "secondary": "#4B92DB"},
    "WAS": {"name": "Washington Commanders", "conf": "NFC", "div": "East",  "primary": "#5A1414", "secondary": "#FFB612"},
}

# Historical / alternate abbreviations mapped onto the current franchise.
ALIASES = {
    "OAK": "LV", "SD": "LAC", "STL": "LAR", "LA": "LAR",
    "WSH": "WAS", "ARZ": "ARI", "BLT": "BAL", "CLV": "CLE",
    "HST": "HOU", "JAC": "JAX", "SL": "LAR", "GNB": "GB",
    "KAN": "KC", "NWE": "NE", "NOR": "NO", "SFO": "SF", "TAM": "TB",
}


def canon(abbr: str) -> str:
    """Normalise any team abbreviation onto the current franchise code."""
    if not abbr:
        return ""
    a = abbr.strip().upper()
    return ALIASES.get(a, a)
