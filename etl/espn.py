"""Fetch player birthplaces from ESPN's public athlete API.

Only the fields we actually plot/show are kept, and every id is cached so
repeat runs are near-instant and easy on ESPN's servers.
"""
from concurrent.futures import ThreadPoolExecutor, as_completed

from . import config, fetch

_CACHE_NAME = "espn_birthplace.json"


def _fetch_one(espn_id):
    try:
        j = fetch.get_json(config.ESPN_ATHLETE.format(espn_id=espn_id),
                           timeout=20, retries=2)
    except Exception:
        return espn_id, None
    bp = j.get("birthPlace") or {}
    return espn_id, {
        "city": bp.get("city"),
        "state": bp.get("state"),
        "country": bp.get("country"),
        "jersey": j.get("jersey"),
        "displayHeight": j.get("displayHeight"),
        "displayWeight": j.get("displayWeight"),
        "experience": (j.get("experience") or {}).get("years"),
    }


def enrich_birthplaces(espn_ids, progress=None):
    """Return {espn_id: {...}} for every id, using cache + threaded fetch."""
    cache = fetch.load_json_cache(_CACHE_NAME)
    ids = [str(i) for i in espn_ids if i]
    todo = [i for i in ids if i not in cache]

    if progress:
        progress(f"ESPN birthplaces: {len(ids) - len(todo)} cached, "
                 f"{len(todo)} to fetch")

    done = 0
    with ThreadPoolExecutor(max_workers=config.ESPN_WORKERS) as pool:
        futures = {pool.submit(_fetch_one, i): i for i in todo}
        for fut in as_completed(futures):
            espn_id, info = fut.result()
            cache[espn_id] = info  # may be None; caches the "no data" outcome
            done += 1
            if progress and done % 100 == 0:
                progress(f"  ...{done}/{len(todo)} ESPN lookups")
                fetch.save_json_cache(_CACHE_NAME, cache)

    fetch.save_json_cache(_CACHE_NAME, cache)
    return {i: cache.get(i) for i in ids}
