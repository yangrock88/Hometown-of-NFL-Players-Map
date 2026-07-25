"""Small stdlib-only HTTP + CSV helpers with on-disk caching."""
import csv
import gzip
import io
import json
import os
import time
import urllib.request
import urllib.error

from . import config


def _request(url, timeout=45):
    req = urllib.request.Request(url, headers={"User-Agent": config.USER_AGENT})
    return urllib.request.urlopen(req, timeout=timeout)


def get_bytes(url, timeout=45, retries=3):
    """GET raw bytes with a few polite retries."""
    last = None
    for attempt in range(retries):
        try:
            with _request(url, timeout) as resp:
                return resp.read()
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
            last = exc
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"Failed to fetch {url}: {last}")


def get_json(url, timeout=30, retries=3):
    return json.loads(get_bytes(url, timeout, retries).decode("utf-8", "replace"))


def download_csv(url, gzipped=False, cache_name=None, max_age_h=12):
    """Fetch a CSV (optionally gzipped) into a list-of-dicts, with a file cache."""
    text = _cached_text(url, gzipped, cache_name, max_age_h)
    return list(csv.DictReader(io.StringIO(text)))


def _cached_text(url, gzipped, cache_name, max_age_h):
    os.makedirs(config.CACHE_DIR, exist_ok=True)
    cache_path = None
    if cache_name:
        cache_path = os.path.join(config.CACHE_DIR, cache_name)
        if os.path.exists(cache_path):
            age_h = (time.time() - os.path.getmtime(cache_path)) / 3600.0
            if age_h < max_age_h:
                with open(cache_path, "r", encoding="utf-8") as fh:
                    return fh.read()

    raw = get_bytes(url)
    text = gzip.decompress(raw).decode("utf-8", "replace") if gzipped \
        else raw.decode("utf-8", "replace")

    if cache_path:
        with open(cache_path, "w", encoding="utf-8") as fh:
            fh.write(text)
    return text


def load_json_cache(name):
    path = os.path.join(config.CACHE_DIR, name)
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except (ValueError, OSError):
            return {}
    return {}


def save_json_cache(name, obj):
    os.makedirs(config.CACHE_DIR, exist_ok=True)
    path = os.path.join(config.CACHE_DIR, name)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh)
