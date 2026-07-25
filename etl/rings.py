"""Count Super Bowl rings per player from historical championship rosters.

A player is credited a ring for each season they appear on the season-ending
roster of that season's Super Bowl winner. Roster membership is the standard
proxy for "earned a ring". Covers seasons back far enough for every player on a
current roster.
"""
from . import config, fetch
from .teams import canon

# NFL season -> Super Bowl-winning franchise (current abbreviation).
SB_WINNERS = {
    2004: "NE", 2005: "PIT", 2006: "IND", 2007: "NYG", 2008: "PIT",
    2009: "NO", 2010: "GB", 2011: "NYG", 2012: "BAL", 2013: "SEA",
    2014: "NE", 2015: "DEN", 2016: "NE", 2017: "PHI", 2018: "NE",
    2019: "KC", 2020: "TB", 2021: "LAR", 2022: "KC", 2023: "KC",
    2024: "PHI",
}


def load_rings(progress=None):
    """Return {gsis_id: number_of_super_bowls_won}."""
    counts = {}
    for season, team in sorted(SB_WINNERS.items()):
        winner = canon(team)
        try:
            rows = fetch.download_csv(
                config.URL_SEASON_ROSTER.format(season=season),
                cache_name=f"roster_{season}.csv", max_age_h=8760)
        except Exception:
            if progress:
                progress(f"  rings: skipped {season} (fetch failed)")
            continue
        for r in rows:
            if canon(r.get("team")) == winner and r.get("gsis_id"):
                gid = r["gsis_id"]
                counts[gid] = counts.get(gid, 0) + 1
    if progress:
        progress(f"rings computed: {sum(counts.values())} across "
                 f"{len(counts)} players ({len(SB_WINNERS)} seasons)")
    fetch.save_json_cache("rings.json", counts)
    return counts
