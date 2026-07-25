"""Scrape each player's *current* contract from their OverTheCap page.

The nflverse contracts feed only tracks a player's largest historical deal, so
veteran one-year contracts (e.g. Carson Wentz's 1yr/$3M) are missing. Each OTC
player page carries a plain-language summary we can parse reliably:

    "Carson Wentz signed a one year, $3 million contract with the Vikings.
     $2.645 million is guaranteed..."

Results are cached in data/cache/otc_contracts.json so re-runs are instant.
"""
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

from . import config, fetch

_CACHE_NAME = "otc_contracts.json"
_WORD_NUM = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
             "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}
_MULT = {"thousand": 1e3, "million": 1e6, "billion": 1e9}


def _money(text):
    m = re.search(r"\$\s?([\d,.]+)\s*(thousand|million|billion)?", text, re.I)
    if not m:
        return None
    num = float(m.group(1).replace(",", ""))
    unit = (m.group(2) or "").lower()
    if unit:
        return num * _MULT[unit]
    return num if num >= 1000 else None  # bare small numbers are ambiguous


def _years(summary):
    m = re.search(r"\b(\d+|one|two|three|four|five|six|seven|eight|nine|ten)\s+year",
                  summary, re.I)
    if not m:
        return None
    tok = m.group(1).lower()
    return int(tok) if tok.isdigit() else _WORD_NUM.get(tok)


def _parse(html):
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text)
    m = re.search(r"signed a (.+?)\.\s", text)
    if not m:
        return None
    summary = m.group(1).strip()
    if "contract" not in summary.lower():
        return None
    value = _money(summary)
    years = _years(summary)
    g = re.search(r"(\$[\d,.]+(?:\s*(?:thousand|million|billion))?\s+is guaranteed)",
                  text, re.I)
    guaranteed = _money(g.group(1)) if g else None
    return {
        "text": summary,
        "years": years,
        "value": value,
        "guaranteed": guaranteed,
        "apy": (value / years) if (value and years) else value,
    }


def _fetch_one(otc_id, url):
    try:
        html = fetch.get_bytes(url, timeout=25, retries=2).decode("utf-8", "replace")
    except Exception:
        return otc_id, None
    return otc_id, _parse(html)


def enrich_contracts(id_url_pairs, progress=None):
    """id_url_pairs: iterable of (otc_id, player_page). Returns {otc_id: {...}}."""
    cache = fetch.load_json_cache(_CACHE_NAME)
    todo = [(oid, url) for (oid, url) in id_url_pairs
            if oid and url and oid not in cache]
    if progress:
        progress(f"OTC contracts: {len(cache)} cached, {len(todo)} to fetch")

    done = 0
    with ThreadPoolExecutor(max_workers=config.OTC_WORKERS) as pool:
        futures = {pool.submit(_fetch_one, oid, url): oid for oid, url in todo}
        for fut in as_completed(futures):
            oid, info = fut.result()
            cache[oid] = info
            done += 1
            if progress and done % 100 == 0:
                progress(f"  ...{done}/{len(todo)} OTC lookups")
                fetch.save_json_cache(_CACHE_NAME, cache)

    fetch.save_json_cache(_CACHE_NAME, cache)
    return cache
