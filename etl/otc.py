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


# A single contract's total value never realistically exceeds ~$0.5B.
_MAX_CONTRACT = 750_000_000


def _money(text):
    m = re.search(r"\$\s?([\d,.]+)\s*(thousand|million|billion)?", text, re.I)
    if not m:
        return None
    num = float(m.group(1).replace(",", ""))
    unit = (m.group(2) or "").lower()
    # OTC occasionally writes full figures with a bogus unit, e.g.
    # "$1,337,500 million". If the number is already a full dollar amount
    # (>= 1000), it's absolute -- ignore any trailing unit word.
    val = num * _MULT[unit] if (unit and num < 1000) else num
    if val < 1000 or val > _MAX_CONTRACT:
        return None
    return val


def _years(summary):
    # allow "four year", "four-year", and OTC typos like "fiver year"
    m = re.search(r"\b(\d+|one|two|three|four|five|six|seven|eight|nine|ten)[a-z]?[\s-]+year",
                  summary, re.I)
    if not m:
        return None
    tok = m.group(1).lower()
    return int(tok) if tok.isdigit() else _WORD_NUM.get(tok)


def derive(summary):
    """Compute {years, value, apy} from a stored contract summary sentence.
    Kept separate from scraping so parser fixes apply to cached text."""
    value = _money(summary or "")
    years = _years(summary or "")
    return {
        "years": years,
        "value": value,
        "apy": (value / years) if (value and years) else value,
    }


def _parse(html):
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text)
    m = re.search(r"signed a (.+?)\.\s", text)
    if not m:
        return None
    summary = m.group(1).strip()
    if "contract" not in summary.lower():
        return None
    g = re.search(r"(\$[\d,.]+(?:\s*(?:thousand|million|billion))?\s+is guaranteed)",
                  text, re.I)
    out = {"text": summary, "guaranteed": _money(g.group(1)) if g else None}
    out.update(derive(summary))
    return out


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

    # Re-derive numbers from each cached summary so parser fixes always apply
    # (guaranteed stays as scraped -- it comes from the full page, not summary).
    out = {}
    for oid, info in cache.items():
        if info and info.get("text"):
            merged = dict(info)
            merged.update(derive(info["text"]))
            out[oid] = merged
        else:
            out[oid] = info
    return out
