"""Build the map dataset from nflverse + ESPN + OverTheCap feeds.

Run via ``python update_data.py``. Everything is cached under data/cache so
re-runs are fast and friendly to upstream servers.
"""
import datetime as _dt
import json
import math
import os
import time

from . import config, fetch, espn, geocode
from .teams import TEAMS, canon

EXCLUDE_STATUS = {"RET", "CUT", "TRT", "UDF"}


def log(msg):
    print(f"[{_dt.datetime.now():%H:%M:%S}] {msg}", flush=True)


# --------------------------------------------------------------------------- #
# Roster: pick each team's most recent *full* week, then dedupe players.
# --------------------------------------------------------------------------- #
def load_current_roster():
    rows = fetch.download_csv(config.URL_ROSTERS, cache_name="roster.csv")
    log(f"roster rows: {len(rows)}")

    # (team, week) -> count, to find each team's latest well-populated week.
    counts = {}
    for r in rows:
        wk = r.get("week")
        tm = canon(r.get("team"))
        if not (wk and wk.isdigit() and tm in TEAMS):
            continue
        counts[(tm, int(wk))] = counts.get((tm, int(wk)), 0) + 1

    team_week = {}
    for (tm, wk), c in counts.items():
        if c >= 30 and wk > team_week.get(tm, -1):
            team_week[tm] = wk
    # fallback: if a team never hit 30 (weird), take its max week seen
    for (tm, wk) in counts:
        if tm not in team_week:
            team_week[tm] = max(w for (t, w) in counts if t == tm)

    log(f"teams resolved: {len(team_week)} (weeks "
        f"{min(team_week.values())}-{max(team_week.values())})")

    # Keep each player's most recent roster row (handles mid-season trades).
    best = {}
    for r in rows:
        tm = canon(r.get("team"))
        wk = r.get("week")
        gid = r.get("gsis_id")
        if not (gid and wk and wk.isdigit() and tm in TEAMS):
            continue
        if int(wk) != team_week.get(tm):
            continue
        if (r.get("status") or "").upper() in EXCLUDE_STATUS:
            continue
        prev = best.get(gid)
        if prev is None or int(wk) > prev["_wk"]:
            r["_wk"] = int(wk)
            r["team"] = tm
            best[gid] = r
    log(f"current roster players: {len(best)}")
    return best


# --------------------------------------------------------------------------- #
# Supporting feeds
# --------------------------------------------------------------------------- #
def load_players_index():
    rows = fetch.download_csv(config.URL_PLAYERS, cache_name="players.csv")
    return {r["gsis_id"]: r for r in rows if r.get("gsis_id")}


def load_starters():
    rows = fetch.download_csv(config.URL_DEPTH, cache_name="depth.csv")
    latest = max((r.get("dt") or "" for r in rows), default="")
    log(f"depth chart date: {latest}")
    best_rank = {}
    for r in rows:
        if r.get("dt") != latest:
            continue
        gid = r.get("gsis_id")
        rank = r.get("pos_rank")
        if not (gid and rank and rank.isdigit()):
            continue
        rank = int(rank)
        cur = best_rank.get(gid)
        if cur is None or rank < cur[0]:
            best_rank[gid] = (rank, r.get("pos_abb"))
    return best_rank


def load_contracts():
    rows = fetch.download_csv(
        config.URL_CONTRACTS, gzipped=True, cache_name="contracts.csv")
    by_otc = {}
    for r in rows:
        otc = r.get("otc_id")
        if not otc:
            continue
        try:
            yr = int(r.get("year_signed") or 0)
        except ValueError:
            yr = 0
        active = (r.get("is_active") or "").lower() in ("true", "1")
        # Prefer active deals; otherwise the most recently signed one.
        score = (1 if active else 0, yr)
        cur = by_otc.get(otc)
        if cur is None or score > cur[0]:
            by_otc[otc] = (score, r)
    return {k: v[1] for k, v in by_otc.items()}


# --------------------------------------------------------------------------- #
# Small helpers
# --------------------------------------------------------------------------- #
def to_float(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def to_int(v):
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return None


def compute_age(birth_date):
    if not birth_date:
        return None
    for fmt in ("%Y-%m-%d", "%m/%d/%Y"):
        try:
            b = _dt.datetime.strptime(birth_date[:10], fmt).date()
            t = _dt.date.today()
            return t.year - b.year - ((t.month, t.day) < (b.month, b.day))
        except ValueError:
            continue
    return None


def fmt_height(inches):
    n = to_int(inches)
    if not n:
        return None
    return f"{n // 12}'{n % 12}\""


def jitter_duplicates(records):
    """Fan out players sharing a hometown so markers don't stack perfectly."""
    groups = {}
    for r in records:
        if r["lat"] is None:
            continue
        key = (round(r["lat"], 3), round(r["lng"], 3))
        groups.setdefault(key, []).append(r)
    for (lat, lng), grp in groups.items():
        if len(grp) == 1:
            continue
        step = 2 * math.pi / len(grp)
        radius = 0.055 + 0.006 * math.log(len(grp) + 1)
        for i, r in enumerate(grp):
            r["lat"] = lat + radius * math.sin(i * step)
            r["lng"] = lng + radius * math.cos(i * step) / math.cos(math.radians(lat))


# --------------------------------------------------------------------------- #
# Assemble
# --------------------------------------------------------------------------- #
def build_records(roster, players, starters, contracts, birthplaces, geo):
    records = []
    missing_geo = 0
    for gid, r in roster.items():
        p = players.get(gid, {})
        espn_id = r.get("espn_id") or p.get("espn_id") or ""
        otc_id = p.get("otc_id") or ""
        team = r["team"]
        meta = TEAMS[team]

        bp = birthplaces.get(str(espn_id)) or {}
        city = bp.get("city")
        state = bp.get("state")
        country = bp.get("country") or "USA"
        geo_res = geo.geocode(city, state, country) if (city or state) else None
        if geo_res:
            lat, lng, prec = geo_res
        else:
            lat = lng = prec = None
            missing_geo += 1

        rank = starters.get(gid)
        draft_round = to_int(p.get("draft_round"))
        c = contracts.get(otc_id, {})

        hometown = None
        if city and state:
            hometown = f"{city}, {state}"
        elif city:
            hometown = city
        elif state:
            hometown = state

        records.append({
            "id": gid,
            "name": r.get("full_name") or p.get("display_name"),
            "team": team,
            "team_name": meta["name"],
            "conf": meta["conf"],
            "div": f"{meta['conf']} {meta['div']}",
            "color": meta["primary"],
            "color2": meta["secondary"],
            "position": r.get("position") or p.get("position"),
            "pos_group": p.get("position_group") or r.get("ngs_position"),
            "jersey": to_int(r.get("jersey_number")) or bp.get("jersey"),
            "height": fmt_height(r.get("height")) or bp.get("displayHeight"),
            "weight": to_int(r.get("weight")),
            "college": r.get("college") or p.get("college_name"),
            "age": compute_age(r.get("birth_date") or p.get("birth_date")),
            "exp": to_int(r.get("years_exp")),
            "headshot": r.get("headshot_url") or p.get("headshot"),
            "espn_id": espn_id or None,
            "espn_url": config.ESPN_PROFILE.format(espn_id=espn_id) if espn_id else None,
            "draft_year": to_int(p.get("draft_year")),
            "draft_round": draft_round,
            "draft_pick": to_int(p.get("draft_pick")),
            "draft_team": canon(p.get("draft_team")) or None,
            "first_round": draft_round == 1,
            "undrafted": draft_round is None and (p.get("draft_year") in (None, "", "NA")),
            "starter": bool(rank and rank[0] == 1),
            "depth_rank": rank[0] if rank else None,
            "depth_pos": rank[1] if rank else None,
            "apy": to_float(c.get("apy")),
            "guaranteed": to_float(c.get("guaranteed")),
            "contract_value": to_float(c.get("value")),
            "contract_years": to_int(c.get("years")),
            "apy_cap_pct": to_float(c.get("apy_cap_pct")),
            "hometown": hometown,
            "home_city": city,
            "home_state": state,
            "home_country": country,
            "lat": lat,
            "lng": lng,
            "geo_precision": prec,
        })
    log(f"records built: {len(records)} (no geo: {missing_geo})")
    return records


def write_outputs(records):
    records.sort(key=lambda r: (r["team"], -(r["apy"] or 0)))
    payload = {
        "generated": _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "season": config.SEASON,
        "count": len(records),
        "teams": TEAMS,
        "players": records,
    }
    os.makedirs(config.ASSETS_DIR, exist_ok=True)
    os.makedirs(config.DATA_DIR, exist_ok=True)
    with open(config.OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False)
    with open(config.OUT_DATA_JS, "w", encoding="utf-8") as fh:
        fh.write("/* Auto-generated by update_data.py. Do not edit by hand. */\n")
        fh.write("window.NFL_DATA = ")
        json.dump(payload, fh, ensure_ascii=False)
        fh.write(";\n")
    log(f"wrote {config.OUT_JSON}")
    log(f"wrote {config.OUT_DATA_JS}")


def main():
    t0 = time.time()
    log("== Hometown of NFL Players :: data build ==")
    roster = load_current_roster()
    players = load_players_index()
    starters = load_starters()
    contracts = load_contracts()

    espn_ids = {r.get("espn_id") or players.get(gid, {}).get("espn_id")
                for gid, r in roster.items()}
    birthplaces = espn.enrich_birthplaces(espn_ids, progress=log)

    geo = geocode.Geocoder()
    records = build_records(roster, players, starters, contracts, birthplaces, geo)
    geo.flush()

    jitter_duplicates(records)
    write_outputs(records)
    log(f"done in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
